from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- Главные страницы ---
    # Home page is now handled in core/urls.py at root level
    path('search/', views.search, name='search'),
    
    # --- Авторизация и Регистрация ---
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pricing/', views.pricing_view, name='pricing'),

    # --- Личный кабинет ---
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/cv/', views.cv_view, name='cv_view'),
    path('profile/cv/download/', views.download_cv_pdf, name='download_cv_pdf'),
    path('application/<int:app_id>/status/<str:status>/', views.update_app_status, name='update_status'),
    
    # --- Работа с вакансиями ---
    path('job/create/', views.create_job, name='create_job'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/apps/', views.view_applications, name='view_applications'),
    path('job/<int:job_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    
    # --- API ENDPOINTS FOR SECURITY DEMONSTRATION (SEC-003, SEC-005, SEC-006) ---
]

# Добавляем API-маршруты только если соответствующие представления реализованы
if hasattr(views, 'api_admin_jobs'):
    urlpatterns.append(path('api/admin/jobs/', views.api_admin_jobs, name='api_admin_jobs'))
if hasattr(views, 'api_student_profile'):
    urlpatterns.append(path('api/student/profile/', views.api_student_profile, name='api_student_profile'))
if hasattr(views, 'api_user_data'):
    urlpatterns.append(path('api/user/<int:user_id>/', views.api_user_data, name='api_user_data'))
if hasattr(views, 'api_register'):
    urlpatterns.append(path('api/register/', views.api_register, name='api_register'))

# --- Сброс пароля ---
urlpatterns += [
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
]