# Django-Allauth OAuth2 Конфигурация для Jobly

## ✅ Сделано

### 1. Обновления в `core/settings.py`

Добавлены следующие параметры для оптимизации потока авторизации OAuth2 через Google:

```python
# Убирает промежуточную страницу подтверждения при входе через соцсети
SOCIALACCOUNT_LOGIN_ON_GET = True

# Автоматически создает аккаунт, если пользователя нет
SOCIALACCOUNT_AUTO_SIGNUP = True

# Не требует подтверждения email при соцсети
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# Заполняет профиль данными из Google автоматически
SOCIALACCOUNT_QUERY_EMAIL = True

# Сохраняет токены для соцсетей
SOCIALACCOUNT_STORE_TOKENS = True
```

### 2. Структура кастомных шаблонов

Все кастомные шаблоны располагаются в:

```
classes-main/
└── templates/
    └── allauth/
        ├── base.html                           # Базовый шаблон
        ├── account/
        │   ├── login.html                      # Страница входа
        │   ├── signup.html                     # Страница регистрации
        │   └── password_reset.html             # Восстановление пароля
        └── socialaccount/
            ├── login.html                      # Подтверждение входа через соцсети
            ├── signup.html                     # Завершение регистрации через соцсети
            └── authentication_error.html       # Обработка ошибок
```

### 3. Созданные шаблоны

#### `templates/allauth/base.html`
- Базовый шаблон со стилизацией Bootstrap 5
- Градиентный фон (purple-violet)
- Адаптивный дизайн (mobile-friendly)
- CSS переменные для кастомизации
- Поддержка лоадеров и анимаций

#### `templates/allauth/account/login.html`
- Кнопка "Войти через Google" с иконкой
- Форма обычного входа
- Ссылка на восстановление пароля
- Ссылка на регистрацию

#### `templates/allauth/account/signup.html`
- Кнопка "Зарегистрироваться через Google"
- Форма регистрации (email, username, пароли)
- Проверка ошибок валидации
- Ссылка на страницу входа

#### `templates/allauth/socialaccount/login.html`
- Страница подтверждения входа через Google
- Отображение email и имени из Google
- Кнопка "Продолжить" для завершения входа

#### `templates/allauth/socialaccount/signup.html`
- Страница завершения регистрации через Google
- Автоматическое заполнение email из Google
- Форма для дополнительных данных

#### `templates/allauth/account/password_reset.html`
- Страница восстановления пароля
- Форма ввода email

#### `templates/allauth/socialaccount/authentication_error.html`
- Обработка ошибок аутентификации
- Понятное сообщение об ошибке
- Контактная информация поддержки

## 🔄 Поток авторизации

### Вход через Google

1. Пользователь кликает "Войти через Google"
2. Перенаправляется на Google (GET запрос)
3. **Благодаря `SOCIALACCOUNT_LOGIN_ON_GET = True`**, 
   промежуточная страница подтверждения пропускается
4. Пользователь выбирает аккаунт Google
5. Google возвращает токен и данные
6. **Благодаря `SOCIALACCOUNT_AUTO_SIGNUP = True`**,
   автоматически создается аккаунт
7. Пользователь авторизуется и перенаправляется на `LOGIN_REDIRECT_URL = '/'`

### Регистрация через Google

1. Пользователь кликает "Зарегистрироваться через Google"
2. Проходит тот же процесс авторизации
3. Если аккаунта нет, показывается `socialaccount/signup.html`
4. Пользователь может заполнить дополнительные данные
5. После отправки формы аккаунт создается
6. Пользователь авторизуется

## 📝 Как переопределить собственный стиль

### Опция 1: Редактирование CSS в `base.html`

Все стили находятся в `<style>` блоке в [templates/allauth/base.html](templates/allauth/base.html).
Просто отредактируйте нужные CSS классы:

```css
/* Изменить цвет градиента */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Изменить размер карточки */
.auth-container {
    max-width: 450px; /* Измените здесь */
}
```

### Опция 2: Использование собственного файла CSS

1. Создайте файл `static/css/allauth.css`
2. Добавьте в `base.html`:
   ```html
   <link rel="stylesheet" href="{% static 'css/allauth.css' %}">
   ```

### Опция 3: Переопределение для конкретной страницы

В каждом шаблоне можно использовать блоки `{% block extra_css %}`:

```html
{% block extra_css %}
<style>
    /* Ваши стили только для этой страницы */
</style>
{% endblock %}
```

## 🛠️ Полезные переменные и хуки

### В `core/settings.py` можно добавить:

```python
# Указать свой адаптер для кастомной логики
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# Указать свой адаптер для обычной авторизации
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'

# Функция для обработки успешной авторизации
SOCIALACCOUNT_SIGNAL_AFTER_SOCIAL_AUTH = 'accounts.signals.on_social_auth'
```

### Создание кастомного адаптера

Если нужна кастомная логика при автозаполнении профиля:

```python
# accounts/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Кастомная логика здесь
        user.first_name = data.get('given_name', '')
        user.last_name = data.get('family_name', '')
        return user
```

## 🧪 Тестирование

### 1. Локальный тест

```bash
python manage.py runserver
# Откройте http://127.0.0.1:8000/accounts/login/
```

### 2. Проверка конфигурации

```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SOCIALACCOUNT_LOGIN_ON_GET)
True
>>> print(settings.SOCIALACCOUNT_AUTO_SIGNUP)
True
```

### 3. Проверка шаблонов

Django автоматически ищет шаблоны в следующем порядке:
1. `templates/` (наш проект) ✅ **Наши кастомные шаблоны здесь**
2. App-specific `templates/` 
3. Встроенные шаблоны allauth (fallback)

Если шаблон не найден, Django покажет ошибку с указанием мест поиска.

## 🚀 Деплой на Render

При деплое убедитесь, что:

1. Переменные окружения установлены:
   ```
   GOOGLE_OAUTH2_KEY=your-key-here
   GOOGLE_OAUTH2_SECRET=your-secret-here
   ALLOWED_HOSTS=jobly.kz,www.jobly.kz
   ```

2. Папка `templates/` включена в Docker образ (см. Dockerfile)

3. Статические файлы собраны:
   ```bash
   python manage.py collectstatic
   ```

## 📞 Интеграция с Google OAuth

### Получение учетных данных

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите OAuth 2.0 API
4. Создайте OAuth 2.0 Client ID (type: Web application)
5. Добавьте авторизованные URI:
   - `http://localhost:8000`
   - `https://jobly.kz`
   - `https://www.jobly.kz`
6. Скопируйте Client ID и Client Secret в переменные окружения

### В Django Admin (http://127.0.0.1:8000/admin/)

1. Перейдите в Sites и убедитесь, что domain правильный
2. Перейдите в Social Applications
3. Создайте новое приложение:
   - Provider: Google
   - Name: Google OAuth
   - Client id: (ваш Client ID)
   - Secret key: (ваш Secret)
   - Sites: выберите правильный сайт

## ⚠️ Возможные проблемы и решения

### 1. "No such table: django_site"

```bash
python manage.py migrate
```

### 2. Шаблоны не обновляются

- Очистите кэш браузера (Ctrl+Shift+Delete)
- Перезагрузите Django сервер
- Проверьте DEBUG = True в settings.py

### 3. Google OAuth не работает на localhost

- Добавьте http://localhost:8000/accounts/google/login/callback/ в Google Console
- Используйте http://, а не https:// для локального тестирования

### 4. Email не заполняется из Google

- Добавьте `SOCIALACCOUNT_QUERY_EMAIL = True` в settings.py
- Убедитесь, что в Google OAuth запрос включает scope 'email'

## 📚 Полезные ссылки

- [Django-allauth документация](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0 документация](https://developers.google.com/identity/protocols/oauth2)
- [Bootstrap 5 документация](https://getbootstrap.com/)
