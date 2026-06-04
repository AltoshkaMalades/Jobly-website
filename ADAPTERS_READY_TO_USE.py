# accounts/adapters.py
# Готовый код - скопируйте в accounts/adapters.py для расширенной функциональности

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class JoblyCustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Кастомный адаптер для Google OAuth2 в Jobly.
    
    Функциональность:
    - Автоматическое заполнение first_name и last_name из Google
    - Логирование новых пользователей
    - Связывание существующих аккаунтов с соцсетью
    """

    def populate_user(self, request, sociallogin, data):
        """
        Заполнить данные User из социального профиля Google.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Заполняем имя и фамилию из Google
        given_name = data.get('given_name', '')
        family_name = data.get('family_name', '')
        
        if given_name:
            user.first_name = given_name
        
        if family_name:
            user.last_name = family_name
        
        # Если есть только полное имя
        if not given_name and 'name' in data:
            name_parts = data.get('name', '').split()
            if name_parts:
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = ' '.join(name_parts[1:])
        
        logger.info(f"User populated: {user.email}, name: {user.first_name} {user.last_name}")
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Сохранить пользователя после входа через Google.
        """
        user = super().save_user(request, sociallogin, form)
        
        if sociallogin.is_new:
            logger.info(f"New user created via Google OAuth: {user.email}")
            # Можно добавить отправку приветственного письма
            # send_welcome_email(user)
        
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Определить, разрешена ли автоматическая регистрация.
        По умолчанию - True для всех.
        """
        # Пример: разрешить регистрацию только некоторым доменам
        email = sociallogin.account.extra_data.get('email', '')
        
        # Разрешить регистрацию для всех доменов
        return True
        
        # ИЛИ ограничить определенными доменами:
        # allowed_domains = ['gmail.com', 'jobly.kz']
        # domain = email.split('@')[1] if '@' in email else ''
        # return domain in allowed_domains


class JoblyCustomAccountAdapter(DefaultAccountAdapter):
    """
    Кастомный адаптер для обычной авторизации в Jobly.
    
    Функциональность:
    - Логирование действий
    - Кастомные сообщения
    - Контроль redirect URLs
    """

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Разрешить ли автоматическую регистрацию через соцсети.
        """
        return True

    def get_login_redirect_url(self, request):
        """
        Получить URL для перенаправления после успешного входа.
        """
        # Может быть переопределено на основе логики
        # return '/dashboard/'
        return super().get_login_redirect_url(request)

    def get_logout_redirect_url(self, request):
        """
        Получить URL для перенаправления после выхода.
        """
        # return '/goodbye/'
        return super().get_logout_redirect_url(request)


# ============================================================================
# ОПЦИОНАЛЬНАЯ РЕГИСТРАЦИЯ СИГНАЛОВ (accounts/signals.py)
# ============================================================================
# Если нужно добавить дополнительную логику при входе через соцсети

"""
# Добавьте это в accounts/signals.py

from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_created
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


@receiver(pre_social_login)
def link_to_existing_user(sender, request, sociallogin, **kwargs):
    '''
    Если пользователь с таким email уже существует,
    связать его социальный аккаунт с существующим пользователем.
    '''
    try:
        email = sociallogin.account.extra_data.get('email')
        if email:
            existing_user = User.objects.get(email=email)
            sociallogin.connect(request, existing_user)
            logger.info(f"Social account linked to existing user: {email}")
    except User.DoesNotExist:
        pass


@receiver(social_account_created)
def on_social_account_created(sender, request, sociallogin, **kwargs):
    '''
    Обработчик при создании нового социального аккаунта.
    '''
    user = sociallogin.user
    logger.info(f"Social account created for {user.email} via {sociallogin.account.provider}")
    # Добавьте дополнительную логику здесь
    # например: создание профиля, отправку email, и т.д.
"""


# ============================================================================
# РЕГИСТРАЦИЯ АДАПТЕРОВ В SETTINGS.PY
# ============================================================================
# Добавьте в core/settings.py:

"""
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.JoblyCustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'accounts.adapters.JoblyCustomAccountAdapter'
"""


# ============================================================================
# РЕГИСТРАЦИЯ СИГНАЛОВ В APPS.PY
# ============================================================================
# accounts/apps.py

"""
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        # Импортируем сигналы при загрузке приложения
        import accounts.signals
"""
