import logging
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Job, Profile, Application, Favorite
from .forms import ProfileForm, JobCreateForm, UserRegisterForm, ApplicationForm
from .tasks import send_welcome_email_task
from .utils import generate_cv_pdf
from .ai_assistant import get_ai_response
from learning.models import Course

# SEC-002: Google OAuth
import requests
import json

# SEC-004: reCAPTCHA
import os

# SEC-005: Security utilities
from .security import log_security_event, get_client_ip, owner_required

CACHE_TTL = 60 * 5

logger = logging.getLogger('django')

# --- ДЕКОРАТОРЫ ---
def role_required(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile, _ = Profile.objects.get_or_create(user=request.user)
            if profile.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            logger.warning(f"Доступ запрещен: {request.user.username}")
            raise PermissionDenied 
        return _wrapped_view
    return decorator

# --- ГЛАВНЫЕ СТРАНИЦЫ ---
def home_page(request):
    cache_key = 'home_page_html'
    cached_html = cache.get(cache_key)
    if cached_html:
        print('[REDIS] Данные успешно взяты из кэша!')
        return HttpResponse(cached_html)

    print('[DB] Запрос идет в базу данных...')
    time.sleep(0.3)
    jobs = Job.objects.select_related('employer').order_by('-created_at')[:6]
    courses = Course.objects.all().order_by('-created_at')[:3]
    response = render(request, 'accounts/index.html', {'jobs': jobs, 'courses': courses})
    cache.set(cache_key, response.content, 60)
    print('[DB] Результат сохранен в кэше на 60 секунд.')
    return response

@cache_page(CACHE_TTL)
def search(request):
    """
    Поиск работ с кэшированием.
    CACHE_TTL: 5 минут
    Категории кэшируются отдельно (60 минут)
    """
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    
    # Cache categories separately
    categories_cache_key = 'accounts:job_categories_all'
    categories = cache.get(categories_cache_key)
    if categories is None:
        categories = list(Job.objects.values_list('category', flat=True).distinct())
        cache.set(categories_cache_key, categories, 60 * 60)  # Cache for 60 minutes
    
    jobs = Job.objects.select_related('employer').order_by('-created_at')
    if query:
        jobs = jobs.filter(title__icontains=query)
    if category:
        jobs = jobs.filter(category=category)
    
    return render(request, 'accounts/search.html', {'jobs': jobs, 'query': query, 'categories': categories})

def job_detail(request, pk):
    """
    Детальная страница вакансии с кэшированием.
    Кэшируется сама работа, но проверки is_favorite/has_applied выполняются для каждого пользователя.
    """
    cache_key = f'accounts:job_detail:{pk}'
    job = cache.get(cache_key)
    
    if job is None:
        job = get_object_or_404(Job.objects.select_related('employer'), pk=pk)
        cache.set(cache_key, job, 60 * 30)  # Cache for 30 minutes
    
    # These checks are user-specific, so we don't cache them
    has_applied = False
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(job=job, user=request.user).exists()
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.role == 'student':
            has_applied = Application.objects.filter(job=job, student=request.user).exists()
    return render(request, 'accounts/job_detail.html', {'job': job, 'has_applied': has_applied, 'is_favorite': is_favorite})

# --- РЕГИСТРАЦИЯ И ВХОД ---
def register(request):
    """
    User registration with SEC-004: Google reCAPTCHA v3
    SEC-005: Log security events
    """
    # По умолчанию берем из GET (если пришли по ссылке), но если в форме выбрали другое — приоритет форме
    role = request.POST.get('role', request.GET.get('role', 'student'))
    captcha_error = None
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        # SEC-004: Verify reCAPTCHA token
        recaptcha_token = request.POST.get('recaptcha_token')
        recaptcha_private_key = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
        
        recaptcha_valid = False
        if recaptcha_token and recaptcha_private_key:
            try:
                response = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data={
                        'secret': recaptcha_private_key,
                        'response': recaptcha_token
                    }
                )
                result = response.json()
                recaptcha_valid = result.get('success', False) and result.get('score', 0) > 0.5
            except Exception as e:
                logger.warning(f"[SEC-004] reCAPTCHA verification failed: {e}")
                captcha_error = "Ошибка проверки reCAPTCHA. Попробуйте позже."
        else:
            # Fallback to simple captcha if reCAPTCHA not configured
            user_captcha = request.POST.get('captcha_input')
            expected_captcha = request.POST.get('captcha_expected')
            if user_captcha != expected_captcha:
                captcha_error = "Неверный код безопасности."
        
        if form.is_valid() and (recaptcha_valid or not recaptcha_private_key) and not captcha_error:
            user = form.save()
            # Вот здесь мы сохраняем выбранную роль в профиль
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            
            # Send welcome email asynchronously; protect registration flow
            try:
                send_welcome_email_task.delay(user.username, user.email)
            except Exception as exc:
                logger.warning('[WARNING] Redis недоступен, таска выполнена синхронно: %s', exc)
                send_welcome_email_task.apply(args=[user.username, user.email])

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            ip_address = get_client_ip(request)
            log_security_event('USER_REGISTERED', user, f'Role: {role}', ip_address)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('home')
        elif not captcha_error:
            # SEC-005: Log failed registration attempt
            ip_address = get_client_ip(request)
            log_security_event('REGISTER_FAILED', request.user if request.user.is_authenticated else None, 
                              f'Errors: {form.errors}', ip_address)
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {
        'form': form, 
        'role': role, 
        'captcha_error': captcha_error
    })

def login_view(request):
    """
    Login view with SEC-005: Security logging
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # SEC-005: Log successful login
            ip_address = get_client_ip(request)
            log_security_event('LOGIN_SUCCESS', user, '', ip_address)
            messages.success(request, "Успешный вход!")
            return redirect('home')
        else:
            # SEC-005: Log failed login attempt
            username = request.POST.get('username', 'unknown')
            ip_address = get_client_ip(request)
            log_security_event('LOGIN_FAILED', None, f'Username: {username}', ip_address)
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'google_oauth_key': os.environ.get('GOOGLE_OAUTH2_KEY', '')
    }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    """
    Logout view with SEC-005: Security logging
    """
    # SEC-005: Log logout
    if request.user.is_authenticated:
        ip_address = get_client_ip(request)
        log_security_event('LOGOUT', request.user, '', ip_address)
    
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect('home')

def verify_email(request):
    """Страница подтверждения почты (заглушка)"""
    return render(request, 'accounts/verify_email.html')

# --- ПРОФИЛЬ ---
@login_required
def profile_view(request):
    """
    Профиль пользователя с кэшированием персональных данных.
    Каждый пользователь имеет собственный кэш профиля (60 минут).
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    context = {'profile': profile}
    
    if profile.role == 'employer':
        # Cache employer's jobs for 30 minutes
        cache_key = f'accounts:profile_jobs_user_{request.user.id}'
        my_jobs = cache.get(cache_key)
        if my_jobs is None:
            my_jobs = list(Job.objects.filter(employer=request.user).select_related('employer'))
            cache.set(cache_key, my_jobs, 60 * 30)
        context['my_jobs'] = my_jobs
    else:
        # Cache student's applications for 15 minutes
        cache_key_apps = f'accounts:profile_applications_user_{request.user.id}'
        my_applications = cache.get(cache_key_apps)
        if my_applications is None:
            my_applications = list(Application.objects.filter(student=request.user).select_related('job', 'job__employer'))
            cache.set(cache_key_apps, my_applications, 60 * 15)
        context['my_applications'] = my_applications
        
        # Cache student's favorites for 15 minutes
        cache_key_fav = f'accounts:profile_favorites_user_{request.user.id}'
        my_favorites = cache.get(cache_key_fav)
        if my_favorites is None:
            my_favorites = list(Favorite.objects.filter(user=request.user).select_related('job', 'job__employer'))
            cache.set(cache_key_fav, my_favorites, 60 * 15)
        context['my_favorites'] = my_favorites
    
    return render(request, 'accounts/profile.html', context)

@login_required
def cv_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/cv.html', {'profile': profile})

@login_required
def download_cv_pdf(request):
    profile = get_object_or_404(Profile, user=request.user)
    pdf_buffer = generate_cv_pdf(profile)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{request.user.username}_cv.pdf"'
    return response

@login_required
def edit_profile(request):
    """
    Редактирование профиля пользователя.
    Инвалидирует: все кэши профиля (jobs, applications, favorites)
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            
            # Invalidate all profile-related caches
            cache.delete(f'accounts:profile_jobs_user_{request.user.id}')
            cache.delete(f'accounts:profile_applications_user_{request.user.id}')
            cache.delete(f'accounts:profile_favorites_user_{request.user.id}')
            
            messages.success(request, "Профиль обновлен.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# --- ВАКАНСИИ И ОТКЛИКИ ---
@login_required
@role_required(allowed_roles=['employer'])
def create_job(request):
    """
    Создание новой вакансии.
    Инвалидирует: кэш категорий и кэш профиля работодателя
    """
    if request.method == 'POST':
        form = JobCreateForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            
            # Invalidate relevant caches
            cache.delete('accounts:job_categories_all')  # Clear categories cache
            cache.delete(f'accounts:profile_jobs_user_{request.user.id}')  # Clear user's jobs cache
            
            messages.success(request, "Вакансия создана успешно!")
            return redirect('profile')
    else:
        form = JobCreateForm()
    return render(request, 'accounts/create_job.html', {'form': form})

@login_required
@role_required(allowed_roles=['student'])
def apply_job(request, pk):
    """
    Подача отклика на вакансию.
    Инвалидирует: кэш профиля студента (мои отклики)
    """
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.student = request.user
            app.save()
            
            # Invalidate profile cache
            cache.delete(f'accounts:profile_applications_user_{request.user.id}')
            # Also invalidate job detail cache (applicant count may have changed)
            cache.delete(f'accounts:job_detail:{pk}')
            
            messages.success(request, "Отклик отправлен!")
            return redirect('job_detail', pk=pk)
    return render(request, 'accounts/apply_job.html', {'job': job})

@login_required
@role_required(allowed_roles=['employer'])
def view_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    apps = Application.objects.filter(job=job).select_related('student', 'job', 'job__employer')
    return render(request, 'accounts/view_applications.html', {'job': job, 'applications': apps})

@login_required
def update_app_status(request, app_id, status):
    """
    Обновление статуса отклика (Принято/Отказ/Просмотрено).
    Инвалидирует: кэш профиля работодателя
    """
    application = get_object_or_404(Application, id=app_id, job__employer=request.user)
    if status in ['accepted', 'rejected', 'viewed']:
        application.status = status
        application.save()
        
        # Invalidate profile cache
        cache.delete(f'accounts:profile_jobs_user_{request.user.id}')
        
        messages.success(request, f"Статус обновлен: {application.get_status_display()}")
    return redirect('view_applications', job_id=application.job.id)

@login_required
def toggle_favorite(request, job_id):
    """
    Добавление/удаление вакансии в избранные.
    Инвалидирует: кэш профиля студента (мои избранные)
    """
    job = get_object_or_404(Job, id=job_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, job=job)
    if not created:
        fav.delete()
    
    # Invalidate profile cache
    cache.delete(f'accounts:profile_favorites_user_{request.user.id}')
    # Also invalidate job detail cache
    cache.delete(f'accounts:job_detail:{job_id}')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@csrf_exempt
@require_POST
def ai_chat(request):
    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    
    ai_response = get_ai_response(user_message)
    return JsonResponse({'response': ai_response})