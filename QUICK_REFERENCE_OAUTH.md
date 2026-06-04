# 🚀 Jobly OAuth2 - Быстрая справка

## ✅ Что было сделано

### 1. **core/settings.py** - Обновлены параметры allauth

```python
SOCIALACCOUNT_LOGIN_ON_GET = True          # ✅ Убирает промежуточный шаг подтверждения
SOCIALACCOUNT_AUTO_SIGNUP = True           # ✅ Автоматически создает аккаунт
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # ✅ Не требует подтверждения email
SOCIALACCOUNT_QUERY_EMAIL = True           # ✅ Заполняет email из Google
SOCIALACCOUNT_STORE_TOKENS = True          # ✅ Сохраняет токены для соцсетей
```

### 2. **Структура папок templates/** создана

```
templates/allauth/
├── base.html                          # Базовый шаблон с Bootstrap 5
├── account/
│   ├── login.html                     # 🔑 Страница входа
│   ├── signup.html                    # 📝 Страница регистрации
│   └── password_reset.html            # 🔐 Восстановление пароля
└── socialaccount/
    ├── login.html                     # ✔️ Подтверждение входа через Google
    ├── signup.html                    # ✔️ Завершение регистрации через Google
    └── authentication_error.html      # ❌ Обработка ошибок
```

### 3. **Документация создана**

- `ALLAUTH_SETUP.md` - **Основная инструкция**
- `ADAPTERS_EXAMPLE.md` - Примеры кастомных адаптеров
- `CSS_CUSTOMIZATION.md` - Примеры CSS кастомизации

---

## 🎯 Быстрый старт

### Шаг 1: Проверить настройки Django

```bash
python manage.py shell
>>> from django.conf import settings
>>> print(f"LOGIN_ON_GET: {settings.SOCIALACCOUNT_LOGIN_ON_GET}")
>>> print(f"AUTO_SIGNUP: {settings.SOCIALACCOUNT_AUTO_SIGNUP}")
```

### Шаг 2: Протестировать локально

```bash
python manage.py runserver
# Откройте http://127.0.0.1:8000/accounts/login/
```

### Шаг 3: Проверить в админке Google OAuth

```bash
python manage.py runserver
# Откройте http://127.0.0.1:8000/admin/
# Соцсети → Social applications → Проверить Google конфиг
```

---

## 📋 Тестовые сценарии

### ✅ Сценарий 1: Вход через Google (новый пользователь)

1. Кликнуть "Войти через Google"
2. **Результат:**
   - ✓ Нет промежуточной страницы подтверждения
   - ✓ Перенаправляется на Google прямо
   - ✓ После выбора аккаунта - автоматический логин
   - ✓ Перенаправляет на `LOGIN_REDIRECT_URL`

### ✅ Сценарий 2: Регистрация через Google

1. Кликнуть "Зарегистрироваться через Google"
2. **Результат:**
   - ✓ Создается новый аккаунт
   - ✓ Email автоматически заполняется из Google
   - ✓ Пользователь авторизуется

### ✅ Сценарий 3: Обычная регистрация

1. Заполнить форму (email, username, пароли)
2. **Результат:**
   - ✓ Аккаунт создан
   - ✓ Пользователь авторизуется
   - ✓ Перенаправляется на главную

---

## 🛠️ Типичные задачи

### Задача 1: Изменить цвета кнопок

**Файл:** `templates/allauth/base.html`

```css
/* Найдите строку */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Измените на нужный цвет, например зеленый */
background: linear-gradient(135deg, #00d084 0%, #00b050 100%);
```

### Задача 2: Добавить собственный логотип

**Файл:** `templates/allauth/base.html`

```html
<!-- Найдите блок .auth-header и добавьте -->
<div class="auth-header">
    <img src="{% static 'images/jobly-logo.png' %}" alt="Jobly" style="width: 100px; margin-bottom: 15px;">
    <h1>Jobly</h1>
    <p>Платформа поиска работы</p>
</div>
```

### Задача 3: Добавить собственный CSS

**Создайте файл:** `static/css/allauth-custom.css`

```css
/* Ваши стили */
.auth-container { max-width: 500px; }
.btn-primary-auth { border-radius: 50px; }
```

**Добавьте в:** `templates/allauth/base.html`

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/allauth-custom.css' %}">
```

### Задача 4: Добавить email подтверждение

**В:** `core/settings.py`

```python
# Измените на:
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # или 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
```

---

## 📊 Структура потока данных

```
1️⃣ Google OAuth Login Flow
   ↓
2️⃣ SOCIALACCOUNT_LOGIN_ON_GET = True
   ↓ Пропускает промежуточный шаг
   ↓
3️⃣ Google возвращает токен + данные
   ↓
4️⃣ SOCIALACCOUNT_AUTO_SIGNUP = True
   ↓ Автоматически создает User + SocialAccount
   ↓
5️⃣ SOCIALACCOUNT_QUERY_EMAIL = True
   ↓ Заполняет email из Google
   ↓
6️⃣ Пользователь авторизуется
   ↓
7️⃣ Перенаправляется на LOGIN_REDIRECT_URL
```

---

## ⚙️ Параметры в settings.py

| Параметр | Значение | Описание |
|----------|----------|---------|
| `SOCIALACCOUNT_LOGIN_ON_GET` | `True` | Убирает подтверждение при GET запросе |
| `SOCIALACCOUNT_AUTO_SIGNUP` | `True` | Автоматическое создание аккаунта |
| `SOCIALACCOUNT_EMAIL_VERIFICATION` | `'none'` | Без проверки email при соцсети |
| `SOCIALACCOUNT_QUERY_EMAIL` | `True` | Запрашивает email у провайдера |
| `SOCIALACCOUNT_STORE_TOKENS` | `True` | Сохраняет токены для повторного использования |
| `ACCOUNT_EMAIL_VERIFICATION` | `'none'` | Без проверки email при обычной регистрации |
| `ACCOUNT_EMAIL_REQUIRED` | `True` | Email обязателен |
| `ACCOUNT_USERNAME_REQUIRED` | `True` | Username обязателен |

---

## 🔗 URLs для тестирования

| URL | Назначение |
|-----|-----------|
| `/accounts/login/` | Страница входа |
| `/accounts/signup/` | Страница регистрации |
| `/accounts/logout/` | Выход |
| `/accounts/password/reset/` | Восстановление пароля |
| `/accounts/google/login/` | Кнопка "Войти через Google" |
| `/admin/socialaccount/socialapp/` | Управление провайдерами (админ) |

---

## 📁 Файлы в проекте

### Основные изменения

```
classes-main/
├── core/
│   └── settings.py  ⭐ Обновлены параметры allauth
├── templates/       ⭐ Новая папка с кастомными шаблонами
│   └── allauth/
│       ├── base.html
│       ├── account/
│       └── socialaccount/
```

### Документация

```
корень проекта/
├── ALLAUTH_SETUP.md          📖 Основная инструкция
├── ADAPTERS_EXAMPLE.md       🔧 Примеры адаптеров
├── CSS_CUSTOMIZATION.md      🎨 CSS примеры
└── QUICK_REFERENCE.md        ⚡ Эта справка
```

---

## 🚨 Возможные проблемы

### ❌ Проблема: Всё еще показывается промежуточный шаг подтверждения

**Решение:**
```python
# core/settings.py
SOCIALACCOUNT_LOGIN_ON_GET = True  # Убедитесь, что True
```

**Затем:**
```bash
python manage.py runserver  # Перезагрузите сервер
```

### ❌ Проблема: Шаблоны не обновляются

**Решение:**
1. Очистить кэш браузера (Ctrl+Shift+Delete)
2. Перезагрузить сервер Django
3. Убедиться, что DEBUG = True

### ❌ Проблема: "TemplateDoesNotExist"

**Решение:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.TEMPLATES[0]['DIRS'])
# Должно быть: [PosixPath('/path/to/templates')]
```

### ❌ Проблема: Google OAuth не работает

**Решение:**
1. Проверить Client ID и Secret в Settings → Environment
2. Добавить callback URL в Google Console
3. Проверить в админке `/admin/socialaccount/socialapp/`

---

## 📞 Команды для управления

### Создать суперюзера
```bash
python manage.py createsuperuser
```

### Посмотреть созданные аккаунты
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
```

### Удалить социальный аккаунт пользователя
```bash
python manage.py shell
>>> from allauth.socialaccount.models import SocialAccount
>>> SocialAccount.objects.filter(user__email='example@gmail.com').delete()
```

---

## 📚 Дополнительные ссылки

- [Django-allauth Docs](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Bootstrap 5](https://getbootstrap.com/)
- [Font Awesome Icons](https://fontawesome.com/)

---

## 💡 Советы

1. **Используйте отдельную конфигурацию для development и production:**
   - Dev: DEBUG = True, ALLOWED_HOSTS = '*'
   - Production: DEBUG = False, ALLOWED_HOSTS = ['jobly.kz']

2. **Всегда используйте HTTPS в production:**
   ```python
   if not DEBUG:
       SECURE_SSL_REDIRECT = True
       SESSION_COOKIE_SECURE = True
   ```

3. **Сохраняйте токены соцсетей для отправки уведомлений:**
   ```python
   SOCIALACCOUNT_STORE_TOKENS = True
   ```

4. **Логируйте события авторизации:**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"User {user.email} logged in via Google")
   ```

---

**Дата создания:** 2026-06-04  
**Статус:** ✅ Полностью настроено и готово к деплою
