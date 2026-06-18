import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
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
        return HttpResponse(cached_html)

    jobs = Job.objects.select_related('employer').order_by('-created_at')[:6]
    courses = Course.objects.all().order_by('-created_at')[:3]
    response = render(request, 'accounts/index.html', {'jobs': jobs, 'courses': courses})
    cache.set(cache_key, response.content, CACHE_TTL)
    return response

@cache_page(CACHE_TTL)
def search(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    jobs = Job.objects.select_related('employer').order_by('-created_at')
    if query:
        jobs = jobs.filter(title__icontains=query)
    if category:
        jobs = jobs.filter(category=category)
    categories = Job.objects.values_list('category', flat=True).distinct()
    return render(request, 'accounts/search.html', {'jobs': jobs, 'query': query, 'categories': categories})

def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('employer'), pk=pk)
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
    # По умолчанию берем из GET (если пришли по ссылке), но если в форме выбрали другое — приоритет форме
    role = request.POST.get('role', request.GET.get('role', 'student'))
    
    # Warn if there are duplicate SocialApp entries (MultipleObjectsReturned issue)
    try:
        from allauth.socialaccount.models import SocialApp
        google_apps = SocialApp.objects.filter(provider='google')
        if google_apps.count() > 1:
            messages.warning(
                request,
                'Warning: Multiple OAuth apps detected. Please run: python manage.py cleanup_socialapps'
            )
    except Exception:
        pass  # Silently ignore errors (allauth not configured, etc.)
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        # Form validation includes reCAPTCHA if configured
        if form.is_valid():
            user = form.save()
            # Вот здесь мы сохраняем выбранную роль в профиль
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
                logger.info('Skip welcome email task dispatch in local/test mode.')
            else:
                send_welcome_email_task.delay(user.username, user.email)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {
        'form': form, 
        'role': role,
    })

def login_view(request):
    context = {}
    
    # Warn if there are duplicate SocialApp entries (MultipleObjectsReturned issue)
    try:
        from allauth.socialaccount.models import SocialApp
        google_apps = SocialApp.objects.filter(provider='google')
        if google_apps.count() > 1:
            messages.warning(
                request,
                'Warning: Multiple OAuth apps detected. Please run: python manage.py cleanup_socialapps'
            )
    except Exception:
        pass  # Silently ignore errors (allauth not configured, etc.)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    context['form'] = form
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

def verify_email(request):
    """Страница подтверждения почты (заглушка)"""
    return render(request, 'accounts/verify_email.html')


def pricing_view(request):
    """Страница с тарифами и подписками"""
    return render(request, 'accounts/pricing.html')


# --- ПРОФИЛЬ ---
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    context = {'profile': profile}
    if profile.role == 'employer':
        context['my_jobs'] = Job.objects.filter(employer=request.user).select_related('employer')
    else:
        context['my_applications'] = Application.objects.filter(student=request.user).select_related('job', 'job__employer')
        context['my_favorites'] = Favorite.objects.filter(user=request.user).select_related('job', 'job__employer')
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
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# --- ВАКАНСИИ И ОТКЛИКИ ---
@login_required
@role_required(allowed_roles=['employer'])
def create_job(request):
    if request.method == 'POST':
        form = JobCreateForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            return redirect('profile')
    else:
        form = JobCreateForm()
    return render(request, 'accounts/create_job.html', {'form': form})

@login_required
@role_required(allowed_roles=['student'])
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.student = request.user
            app.save()
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
    """Обновление статуса отклика (Принято/Отказ)"""
    application = get_object_or_404(Application, id=app_id, job__employer=request.user)
    if status in ['accepted', 'rejected', 'viewed']:
        application.status = status
        application.save()
        messages.success(request, f"Статус обновлен: {application.get_status_display()}")
    return redirect('view_applications', job_id=application.job.id)

@login_required
def toggle_favorite(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, job=job)
    if not created:
        fav.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@csrf_exempt
@require_POST
def ai_chat(request):
    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    
    ai_response = get_ai_response(user_message)
    return JsonResponse({'response': ai_response})