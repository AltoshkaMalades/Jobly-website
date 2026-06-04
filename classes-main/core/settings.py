import os
import sys
from pathlib import Path
from celery.schedules import crontab
import dj_database_url  

# Базовые директории
BASE_DIR = Path(__file__).resolve().parent.parent

# --- БЕЗОПАСНОСТ    ---
SECRET_KEY = 'django-insecure-your-very-secret-key-here' 

DEBUG = True 

ALLOWED_HOSTS = ['*']

# --- ПРИЛОЖЕНИЯ ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'embed_video',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_recaptcha',  # SEC-004: Google reCAPTCHA
    'accounts',
    'learning',
]

SITE_ID = 1

# 1. КАСТОМНОЕ ХЕШИРОВАНИЕ (Argon2 вместо стандартного PBKDF2)
# Не забудь выполнить: pip install argon2-cffi
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'accounts.middleware.EndpointRateLimitMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls' 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# --- БАЗА ДАННЫХ ---
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    ) if os.environ.get('DATABASE_URL') else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Read full Redis URL from environment when available (e.g. on Render).
# Fallback to the Docker service name 'redis' for local development.
# NOTE: We use separate Redis databases:
#   - DB 0: Celery (broker and result backend)
#   - DB 1: Django Cache
REDIS_BASE_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')
REDIS_CELERY_URL = os.environ.get('CELERY_BROKER_URL', f'{REDIS_BASE_URL}/0')
REDIS_CACHE_URL = os.environ.get('REDIS_CACHE_URL', f'{REDIS_BASE_URL}/1')

IS_TESTING = os.environ.get('DJANGO_TESTING') == '1' or any(
    'pytest' in arg or 'test' in arg for arg in sys.argv
)

# Use in-memory cache for development/testing, Redis for production
if IS_TESTING or not os.environ.get('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_CACHE_URL,
            'KEY_PREFIX': 'django-cache',
            'TIMEOUT': 300,  # 5 минут по умолчанию
        }
    }


# --- ВАЛИДАЦИЯ ПАРОЛЕЙ ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- ИНТЕРНАЦИОНАЛИЗАЦИЯ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

# --- СТАТИКА ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 2. НАСТРОЙКИ HTTPS И ЗАЩИТЫ (Пункт 3 задания)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# 3. ЛОГИРОВАНИЕ ДЕЙСТВИЙ (Пункт 4 задания)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Celery should prefer explicit env vars, otherwise use the same REDIS_URL.
# NOTE: Celery uses DB 0 (separate from Django Cache which uses DB 1)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_CELERY_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_CELERY_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = IS_TESTING
CELERY_TASK_EAGER_PROPAGATES = IS_TESTING
CELERY_BEAT_SCHEDULE = {
    'daily-job-digest-at-midnight': {
        'task': 'accounts.tasks.daily_job_digest_task',
        'schedule': crontab(hour=0, minute=0),
        'args': (),
    },
    'cleanup-old-sessions-every-15-minutes': {
        'task': 'accounts.tasks.cleanup_old_sessions_task',
        'schedule': 15 * 60,
        'args': (),
    },
}
# --- ВАЖНОЕ ДОПОЛНЕНИЕ ---
# Указываем Django, куда перенаправлять неавторизованных пользователей
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ============================================================================
# SEC-002: Google OAuth 2.0 Configuration via django-allauth
# ============================================================================
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH2_KEY', ''),
            'secret': os.environ.get('GOOGLE_OAUTH2_SECRET', ''),
            'key': '',
        },
    }
}

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

# ============================================================================
# SEC-004: Google reCAPTCHA v3 Configuration
# ============================================================================
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']  # Allow test keys in development

# ============================================================================
# SEC-007: Secret Scanning Configuration
# ============================================================================
# Трufflehog будет сканировать репо в CI/CD
SECRETS_LOCATION = os.path.join(BASE_DIR, '..')  # Scan from repo root