# SEC-006: Настройка заголовков безопасности и Google OAuth

## ✅ Выполненные задачи

### 1. Настройка заголовков безопасности

**Файл:** `core/settings.py`

Обновлены параметры безопасности для production (блок `if not DEBUG:`):

- **HTTP Strict Transport Security (HSTS)**
  - `SECURE_HSTS_SECONDS = 31536000` (1 год)
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
  - `SECURE_HSTS_PRELOAD = True`

- **Content Security & XSS Protection**
  - `SECURE_CONTENT_TYPE_NOSNIFF = True`
  - `SECURE_BROWSER_XSS_FILTER = True`
  - `X_FRAME_OPTIONS = 'DENY'`

- **Referrer Policy**
  - `SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'`

- **SSL & Cookies**
  - `SECURE_SSL_REDIRECT = True`
  - `SESSION_COOKIE_SECURE = True`
  - `CSRF_COOKIE_SECURE = True`

### 2. Content-Security-Policy (CSP) заголовок

**Файл:** `accounts/middleware.py`

Создан новый `SecurityHeadersMiddleware` который добавляет:

- **Permissions-Policy** - ограничивает доступ браузера к:
  - camera=() - камера
  - microphone=() - микрофон
  - geolocation=() - геолокация
  - payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), vr=(), xr-spatial-tracking=()

- **Content-Security-Policy (CSP)** - разрешает контент только с:
  - 'self' - текущий домен
  - Google OAuth и рекапча
  - CDN для стилей и шрифтов
  - Запрещает XSS и injection атаки

Middleware добавлен в `MIDDLEWARE` список в settings.py.

### 3. Автонастройка Google OAuth

**Файл:** `accounts/management/commands/setup_google_oauth.py`

Создана Django management команда для автоматической настройки Google OAuth:

```bash
# Использование с параметрами по умолчанию (jobly.kz)
python manage.py setup_google_oauth

# Или с пользовательскими параметрами
python manage.py setup_google_oauth \
  --client-id "909443104126-baj9tq8uhj7tb6fg3vv8d9vvg03c7qr4.apps.googleusercontent.com" \
  --secret "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" \
  --domain "jobly.kz"
```

**Что делает команда:**
1. ✅ Находит или создает Site с id=1 и доменом jobly.kz
2. ✅ Создает или обновляет SocialApp для провайдера Google
3. ✅ Привязывает SocialApp к Site через ManyToMany связь
4. ✅ Логирует все шаги выполнения

**Результат:** Исправляет ошибку `DoesNotExist` на `/login/` на production, так как:
- Site всегда будет существовать с правильным доменом
- SocialApp будет привязана к правильному сайту
- Тег `{% provider_login_url %}` будет находить приложение без ошибок

## 🚀 Инструкция по развертыванию на Render.com

1. **На production сервере выполните одну команду:**
   ```bash
   python manage.py setup_google_oauth
   ```

2. **Или добавьте в `release` фазу deploy (если используете Procfile):**
   ```
   web: python manage.py collectstatic --noinput && python manage.py setup_google_oauth && gunicorn core.wsgi
   ```

3. **После этого запустите сервер:**
   - Сайт будет доступен по https://jobly.kz
   - HSTS, CSP и Permissions-Policy заголовки автоматически добавятся
   - Google OAuth будет работать без DoesNotExist ошибок

## ✨ Проверка результата

### На securityheaders.com

Site должен получить оценку **A** или **A+** за:
- ✅ HSTS (Strict-Transport-Security)
- ✅ CSP (Content-Security-Policy)
- ✅ Permissions-Policy
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ Referrer-Policy: strict-origin-when-cross-origin

### Локально (для проверки)

```bash
# Проверить middleware работает
curl -i https://jobly.kz/login/

# Должны увидеть заголовки:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# Content-Security-Policy: default-src 'self'; ...
# Permissions-Policy: camera=(), microphone=(), geolocation=(), ...
# X-Frame-Options: DENY
```

## 📝 Конфигурация

Все настройки находятся в:
- `core/settings.py` - основные параметры HSTS, SSL, CSRF
- `accounts/middleware.py` - middleware для заголовков CSP и Permissions-Policy
- `accounts/management/commands/setup_google_oauth.py` - команда автонастройки

Конфликтующая секция 'APP' в `SOCIALACCOUNT_PROVIDERS` удалена - теперь конфигурация берется из базы данных.
