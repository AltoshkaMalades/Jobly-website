"""
Security utilities for access control (SEC-005)
Проверка владельца ресурса и управление правами доступа
"""
import logging
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

logger = logging.getLogger('django')

# ============================================================================
# SEC-005: Проверка владельца ресурса (Access Control)
# ============================================================================

def owner_required(resource_param='pk', owner_field='employer'):
    """
    Декоратор для проверки владельца ресурса.
    
    Использование:
        @owner_required('job_id', 'employer')
        def edit_job(request, job_id):
            job = Job.objects.get(pk=job_id)
    
    Args:
        resource_param (str): Имя параметра URL (по умолчанию 'pk')
        owner_field (str): Имя поля владельца в модели (по умолчанию 'employer')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            resource_id = kwargs.get(resource_param)
            
            # Получить модель и имя из view_func
            if 'job' in view_func.__name__.lower():
                from accounts.models import Job
                try:
                    resource = Job.objects.get(pk=resource_id)
                    owner = getattr(resource, owner_field)
                except Job.DoesNotExist:
                    logger.warning(f"[SEC-005] Job {resource_id} not found")
                    raise PermissionDenied("Ресурс не найден")
            
            # Проверка владельца
            if owner != request.user and not request.user.is_superuser:
                logger.warning(
                    f"[SEC-005] Access denied: user {request.user.id} "
                    f"tried to access {view_func.__name__} for resource owned by {owner.id}"
                )
                raise PermissionDenied("У вас нет прав доступа к этому ресурсу")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def student_profile_check(view_func):
    """
    Декоратор для проверки что студент редактирует только свой профиль
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_id = kwargs.get('user_id') or request.user.id
        
        if int(user_id) != request.user.id and not request.user.is_superuser:
            logger.warning(
                f"[SEC-005] Profile access denied: user {request.user.id} "
                f"tried to access profile of user {user_id}"
            )
            raise PermissionDenied("Вы можете редактировать только свой профиль")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def log_security_event(event_type, user, details=None, ip_address=None):
    """
    Логирование события безопасности (SEC-005)
    
    Args:
        event_type (str): Тип события (login, logout, access_denied, etc)
        user: User object
        details (str): Дополнительные детали
        ip_address (str): IP адрес пользователя
    """
    message = f"[SECURITY] {event_type} | User: {user.id} ({user.username})"
    
    if ip_address:
        message += f" | IP: {ip_address}"
    
    if details:
        message += f" | Details: {details}"
    
    logger.warning(message)


def get_client_ip(request):
    """
    Получить IP адрес клиента из request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
