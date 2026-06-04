# Week 3 Security Implementation (SEC-002 to SEC-007)

## ✅ Что было реализовано

### SEC-002: Google OAuth 2.0 ✅
**Файлы:** 
- `core/settings.py` — Конфигурация Google OAuth
- `accounts/models.py` — Поле `google_id` и `is_oauth_user` в Profile
- `accounts/views.py` — Функция `google_oauth_callback()`
- `accounts/urls.py` — URL для Google OAuth
- `core/urls.py` — Include social_django URLs
- `requirements.txt` — `social-auth-app-django==5.4.0`

**Как это работает:**
1. Пользователь нажимает "Войти через Google"
2. social_django перенаправляет на Google
3. После авторизации Google возвращает токен
4. `google_oauth_callback()` автоматически создаёт/обновляет профиль
5. Пользователь залогирован и приветствуется

**Демонстрация:**
```bash
# Для локальной разработки нужны:
# GOOGLE_OAUTH2_KEY = "ххххххххххххххххххх.apps.googleusercontent.com"
# GOOGLE_OAUTH2_SECRET = "GOCSPX-ххххххххххххххххххх"
```

---

### SEC-004: Google reCAPTCHA v3 ✅
**Файлы:**
- `requirements.txt` — `django-recaptcha==4.0.0`
- `core/settings.py` — Конфигурация reCAPTCHA
- `accounts/views.py` — Верификация токена в `register()`
- `accounts/views.py` — Fallback на простую CAPTCHA если не настроена

**Как это работает:**
1. На фронтенде добавляется Google reCAPTCHA скрипт
2. При отправке формы генерируется токен
3. Бэкенд отправляет токен на серверы Google для проверки
4. Если score > 0.5 — регистрация разрешена
5. Если score < 0.5 — запросить повторную попытку (бот!)

**Демонстрация:**
```bash
# Для локальной разработки нужны:
# RECAPTCHA_PUBLIC_KEY = "6Ldxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# RECAPTCHA_PRIVATE_KEY = "6Ldxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Без ключей:** Система переходит на простую CAPTCHA (fallback)

---

### SEC-005: Проверки владельца (Access Control) ✅
**Файлы:**
- `accounts/security.py` — Утилиты для проверки прав (NEW)
- `accounts/views.py` — Логирование безопасности на всех эндпоинтах
- `accounts/models.py` — Поле `is_oauth_user` для аудита

**Реализовано:**
- ✅ `@owner_required` декоратор для проверки владельца
- ✅ `@student_profile_check` для защиты профилей студентов
- ✅ Логирование всех событий безопасности (login, logout, register и т.д.)
- ✅ IP-адреса записываются в логи
- ✅ Неудачные попытки входа логируются
- ✅ Все операции CRUD защищены проверками прав

**Логи находятся в:** `debug.log`

**Пример лога:**
```
[SECURITY] LOGIN_FAILED | User: None | IP: 192.168.1.1 | Details: Username: hacker
[SECURITY] LOGIN_SUCCESS | User: 5 (john_doe) | IP: 192.168.1.2
[SECURITY] LOGOUT | User: 5 (john_doe) | IP: 192.168.1.2
[SECURITY] USER_REGISTERED | User: 6 (new_user) | IP: 192.168.1.3 | Details: Role: student
```

---

### SEC-006: Заголовки безопасности ✅
**Файлы:** `core/settings.py`

**Реализовано:**
- ✅ `SECURE_SSL_REDIRECT = True` (Force HTTPS)
- ✅ `SESSION_COOKIE_SECURE = True` (HTTPS only)
- ✅ `CSRF_COOKIE_SECURE = True` (HTTPS only)
- ✅ `SECURE_HSTS_SECONDS = 31536000` (1 год)
- ✅ `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- ✅ `SECURE_HSTS_PRELOAD = True` (для HSTS preload list)
- ✅ `SECURE_BROWSER_XSS_FILTER = True`
- ✅ `SECURE_CONTENT_TYPE_NOSNIFF = True`

**Проверка:** Откройте https://securityheaders.com и вставьте URL сайта

**Ожидаемая оценка:** A или B+

---

### SEC-007: Аудит секретов (Trufflehog) ✅
**Файлы:**
- `scripts/audit_secrets.sh` — Скрипт для сканирования (NEW)
- `requirements.txt` — Зависимости уже добавлены в CI/CD

**Как использовать:**
```bash
# Запустить сканирование
bash scripts/audit_secrets.sh

# Результаты сохранятся в: trufflehog_scan_YYYYMMDD_HHMMSS.json
```

**Что проверяет:**
- ✅ Git историю на утечки (SECRET_KEY, API ключи и т.д.)
- ✅ .env файлы (проверка что они в .gitignore)
- ✅ Критичные файлы на регулярные выражения для секретов
- ✅ Паттерны: PASSWORD, API_KEY, PRIVATE_KEY, DATABASE_URL и т.д.

**Результат:** "Секретов не найдено" или список найденных проблем

---

## 📋 ЧТО НУЖНО ДЛЯ ЗАПУСКА

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Создать миграцию для Profile (новые поля)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Установить переменные окружения (.env)

**Для локальной разработки:**
```bash
# .env файл
GOOGLE_OAUTH2_KEY=your_google_key_here
GOOGLE_OAUTH2_SECRET=your_google_secret_here
RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI  # Test key
RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe  # Test key
```

**Тестовые ключи reCAPTCHA (всегда проходят):**
- Public: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI`
- Private: `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`

---

## 🎯 ДЕМОНСТРАЦИЯ ДЛЯ ПРЕПОДАВАТЕЛЯ

### Demo 1: Google OAuth
```bash
1. Открыть сайт
2. Нажать "Войти через Google"
3. Авторизоваться через Google аккаунт
4. Показать что Profile создан с is_oauth_user=True
5. Показать логи: [SECURITY] OAUTH_LOGIN
```

### Demo 2: reCAPTCHA
```bash
1. Открыть страницу регистрации
2. Нажать F12 (Network tab)
3. Заполнить форму и отправить
4. Показать что отправляется recaptcha_token в body
5. Показать POST запрос на https://www.google.com/recaptcha/api/siteverify
```

### Demo 3: Security Logging
```bash
1. Попробовать залогиниться с неправильным паролем
2. Показать в debug.log: [SECURITY] LOGIN_FAILED | IP: xxx
3. Залогиниться правильно
4. Показать: [SECURITY] LOGIN_SUCCESS | IP: xxx
5. Выйти из системы
6. Показать: [SECURITY] LOGOUT | IP: xxx
```

### Demo 4: Access Control
```bash
1. Работодатель создает вакансию
2. Студент пытается редактировать эту вакансию
3. Показать 403 Forbidden
4. Показать в логах: [SEC-005] Access denied
```

### Demo 5: reCAPTCHA проверка
```bash
1. Открыть https://www.google.com/recaptcha/admin/create
2. Создать reCAPTCHA v3 проект
3. Получить PUBLIC_KEY и SECRET_KEY
4. Добавить в .env
5. Перезагрузить сайт
6. На странице регистрации должна быть reCAPTCHA бэйдж
```

### Demo 6: Trufflehog сканирование
```bash
1. Запустить: bash scripts/audit_secrets.sh
2. Показать результаты
3. Показать JSON файл с результатами
4. Результат: "Секретов не найдено"
```

### Demo 7: Заголовки безопасности
```bash
1. Открыть curl или Postman
2. Сделать GET запрос к сайту
3. Показать Headers:
   - Strict-Transport-Security: max-age=31536000
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
4. Открыть https://securityheaders.com
5. Вставить URL сайта
6. Показать оценку: A или B+
```

---

## 📊 СХЕМА ВЗАИМОДЕЙСТВИЯ

### Google OAuth Flow
```
User → "Login with Google" 
  → social_django redirects to Google
  → Google OAuth Page
  → User authorizes
  → Google returns code + id_token
  → social_django exchanges for access_token
  → google_oauth_callback() creates/updates Profile
  → User is logged in ✅
```

### reCAPTCHA v3 Flow
```
User fills registration form
  → Client generates reCAPTCHA token
  → Submit form with token
  → Backend sends token to Google API
  → Google returns score (0-1)
  → Score > 0.5 → Registration allowed ✅
  → Score < 0.5 → Retry (suspected bot) ❌
```

### Security Logging Flow
```
Every action:
  → login_view()
  → apply_job()
  → create_job()
  → toggle_favorite()
  → Any auth event
  
  → get_client_ip(request)
  → log_security_event(type, user, details, ip)
  → Written to debug.log with timestamp + IP
```

---

## 🔧 КОНФИГУРАЦИЯ

### settings.py SEC-002
```python
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Google OAuth
    'django.contrib.auth.backends.ModelBackend',  # Standard Django auth
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET', '')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'home'
```

### settings.py SEC-004
```python
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
```

### settings.py SEC-006
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

## ❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ

**Q: Как получить Google OAuth ключи?**
A: https://console.cloud.google.com/ → Create Project → OAuth 2.0 Client ID

**Q: Как получить reCAPTCHA ключи?**
A: https://www.google.com/recaptcha/admin/create → Select reCAPTCHA v3 → Create

**Q: Почему reCAPTCHA не работает локально?**
A: Использованы тестовые ключи, которые всегда работают

**Q: Где находятся логи безопасности?**
A: `debug.log` в корне проекта

**Q: Как проверить что проверки доступа работают?**
A: Попробуйте редактировать чужую вакансию → 403 Forbidden

---

## ✅ ЧЕКЛИСТ ПЕРЕД ВЫСТАВКОЙ

- [ ] Установлены все пакеты (pip install -r requirements.txt)
- [ ] Запущены миграции (python manage.py migrate)
- [ ] .env содержит Google OAuth ключи
- [ ] .env содержит reCAPTCHA ключи (можно тестовые)
- [ ] Протестирована регистрация через Google OAuth
- [ ] Протестирована регистрация обычным способом
- [ ] Проверены логи безопасности в debug.log
- [ ] Запущено: bash scripts/audit_secrets.sh
- [ ] Результат: "Секретов не найдено"
- [ ] Проверены заголовки безопасности на securityheaders.com
- [ ] Оценка: A или B+

---

**Всё готово к демонстрации! 🚀**
