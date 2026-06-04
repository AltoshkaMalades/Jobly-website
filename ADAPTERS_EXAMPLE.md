# Кастомные адаптеры для Django-Allauth
# Поместите этот файл в accounts/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import User
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Кастомный адаптер для обработки входа через соцсети.
    Автоматически заполняет профиль пользователя данными из Google.
    """

    def populate_user(self, request, sociallogin, data):
        """
        Заполнить данные пользователя из социального профиля.
        
        Args:
            request: HTTP request
            sociallogin: Информация о социальном логине
            data: Данные из профиля провайдера (Google)
        
        Returns:
            User: Заполненный объект пользователя
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Заполняем имя и фамилию из Google
        user.first_name = data.get('given_name', '')
        user.last_name = data.get('family_name', '')
        
        # Если есть полное имя, но нет отдельных компонентов
        if 'name' in data and not user.first_name:
            name_parts = data.get('name', '').split()
            if len(name_parts) > 0:
                user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = ' '.join(name_parts[1:])
        
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Сохранить пользователя после входа через соцсети.
        Можно добавить дополнительную логику здесь.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Логируем создание нового пользователя
        if sociallogin.is_new:
            logger.info(f"Новый пользователь создан через {sociallogin.account.provider}: {user.email}")
            
            # Можно отправить приветственное письмо
            try:
                send_mail(
                    subject='Добро пожаловать на Jobly!',
                    message=f'Привет, {user.first_name}! Рады видеть тебя на платформе Jobly.',
                    from_email='noreply@jobly.kz',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке приветственного письма: {e}")
        
        return user

    def get_app(self, request, provider, client_id=None):
        """
        Получить конфигурацию приложения провайдера.
        Можно добавить кастомную логику выбора app.
        """
        app = super().get_app(request, provider, client_id)
        return app


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Кастомный адаптер для обработки обычной авторизации и регистрации.
    """

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Определить, разрешена ли автоматическая регистрация.
        По умолчанию - да, но можно добавить проверки.
        """
        # Пример: разрешить auto-signup только для определенных доменов
        email = sociallogin.account.extra_data.get('email', '')
        
        # Разрешить все домены
        return True

    def save_user(self, request, sociallogin, form=None):
        """
        Сохранить пользователя при регистрации.
        """
        user = super().save_user(request, sociallogin, form)
        return user

    def get_login_redirect_url(self, request):
        """
        Получить URL для перенаправления после успешной авторизации.
        """
        # По умолчанию перенаправляет на LOGIN_REDIRECT_URL
        return super().get_login_redirect_url(request)


# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ СИГНАЛЫ (signals.py)
# ============================================================================
# Если нужна кустомная обработка событий, добавьте эти сигналы в accounts/signals.py

from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_created


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """
    Сигнал перед логином через соцсети.
    Можно использовать для связывания существующих пользователей.
    """
    try:
        email = sociallogin.account.extra_data.get('email')
        if email:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
            logger.info(f"Профиль соцсети связан с существующим пользователем: {email}")
    except User.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Ошибка при связывании профилей: {e}")


@receiver(social_account_created)
def on_social_account_created(sender, request, sociallogin, **kwargs):
    """
    Сигнал после создания нового социального аккаунта.
    """
    logger.info(f"Социальный аккаунт создан: {sociallogin.account.provider}")


# ============================================================================
# РЕГИСТРАЦИЯ СИГНАЛОВ (в accounts/apps.py)
# ============================================================================
"""
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals  # Импортируем сигналы при загрузке приложения
"""
