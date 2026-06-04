# 📋 Чек-лист: OAuth2 Google для Jobly

## ✅ ЭТАП 1: Разработка (Development)

### Конфигурация Django
- [ ] `SOCIALACCOUNT_LOGIN_ON_GET = True` в settings.py
- [ ] `SOCIALACCOUNT_AUTO_SIGNUP = True` в settings.py
- [ ] `SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'` в settings.py
- [ ] `SOCIALACCOUNT_QUERY_EMAIL = True` в settings.py
- [ ] `DEBUG = True` для разработки
- [ ] `ALLOWED_HOSTS = ['*']` или `['localhost', '127.0.0.1']`

### Структура папок
- [ ] Папка `templates/allauth/` создана
- [ ] `templates/allauth/base.html` существует
- [ ] `templates/allauth/account/login.html` существует
- [ ] `templates/allauth/account/signup.html` существует
- [ ] `templates/allauth/socialaccount/login.html` существует
- [ ] `templates/allauth/socialaccount/signup.html` существует

### Тестирование функциональности
```bash
# Запустите эти команды
python manage.py runserver
```

- [ ] http://127.0.0.1:8000/accounts/login/ открывается без ошибок
- [ ] Видна кнопка "Войти через Google"
- [ ] Клик на кнопку перенаправляет на Google (не на подтверждение)
- [ ] http://127.0.0.1:8000/accounts/signup/ открывается без ошибок
- [ ] Видна кнопка "Зарегистрироваться через Google"
- [ ] Дизайн шаблонов выглядит красиво (Bootstrap стили загружены)

### Проверка конфигурации
```bash
python manage.py shell
```

- [ ] `from django.conf import settings`
- [ ] `print(settings.SOCIALACCOUNT_LOGIN_ON_GET)` → `True`
- [ ] `print(settings.SOCIALACCOUNT_AUTO_SIGNUP)` → `True`

### Google OAuth2 настройка (localhost)
- [ ] Google Cloud Console доступен
- [ ] OAuth 2.0 Client ID создан
- [ ] Авторизованные URI включают: `http://localhost:8000`
- [ ] Callback URL: `http://localhost:8000/accounts/google/login/callback/`

### Django Admin
```bash
python manage.py runserver
# Откройте http://127.0.0.1:8000/admin/
```

- [ ] Суперюзер создан (`python manage.py createsuperuser`)
- [ ] В Admin → Sites проверить domain (должен быть `localhost:8000` или `example.com`)
- [ ] В Admin → Social Applications:
  - [ ] Создана запись для Google
  - [ ] Provider: `google`
  - [ ] Name: `Google OAuth`
  - [ ] Client id: вставлен
  - [ ] Secret key: вставлен
  - [ ] Sites: выбран правильный сайт

### Функциональное тестирование (с реальным Google аккаунтом)
- [ ] Попытаться войти через Google
- [ ] ✓ Нет промежуточной страницы подтверждения
- [ ] ✓ Google открывается в новой вкладке
- [ ] ✓ После выбора аккаунта - автоматический логин
- [ ] ✓ Перенаправление на `LOGIN_REDIRECT_URL = '/'`
- [ ] ✓ Пользователь появился в BD (`python manage.py shell` → `User.objects.all()`)

---

## ✅ ЭТАП 2: Production (Render.com или сервер)

### Переменные окружения
- [ ] `GOOGLE_OAUTH2_KEY` установлена
- [ ] `GOOGLE_OAUTH2_SECRET` установлена
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS = ['jobly.kz', 'www.jobly.kz']`
- [ ] `SECRET_KEY` установлена (сильная)
- [ ] `DATABASE_URL` установлена (PostgreSQL рекомендуется)

### SSL/TLS
- [ ] HTTPS включен (сертификат валиден)
- [ ] `SECURE_SSL_REDIRECT = True` в settings.py
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`

### Django Security
- [ ] `SECRET_KEY` не в коде (использует переменные окружения)
- [ ] `DEBUG = False` в production
- [ ] Все пароли и ключи в `.env`
- [ ] `.env` в `.gitignore`

### Google OAuth2 Production
- [ ] Google Cloud Console обновлена
- [ ] Авторизованные URI включают: `https://jobly.kz` и `https://www.jobly.kz`
- [ ] Callback URL: `https://jobly.kz/accounts/google/login/callback/`
- [ ] OAuth2 Screen в Google Console настроена (logo, брендинг)

### Django Admin в Production
- [ ] В Admin → Sites обновлен domain на `jobly.kz`
- [ ] В Admin → Social Applications обновлена запись:
  - [ ] Client id обновлен (production credentials)
  - [ ] Secret key обновлен (production credentials)
  - [ ] Sites переназначены на production домен

### Статические файлы
- [ ] `python manage.py collectstatic` выполнен
- [ ] `STATIC_URL` правильный
- [ ] `STATIC_ROOT` правильный
- [ ] CSS и шрифты загружаются правильно

### База данных
- [ ] Миграции применены: `python manage.py migrate`
- [ ] `django_site` таблица заполнена правильно
- [ ] `socialaccount_socialapp` таблица заполнена

### Логирование
- [ ] Логирование настроено в settings.py
- [ ] Логи записываются в файл: `python manage.py shell` → проверить работу
- [ ] Email для ошибок настроен (ADMINS)

### Docker (если используется)
- [ ] Dockerfile содержит `COPY templates/ /app/templates/`
- [ ] docker-compose.yml содержит все переменные окружения
- [ ] `docker build` и `docker run` выполняются без ошибок

### Render.com (если используется)
- [ ] Environment variables добавлены в Render Dashboard
- [ ] Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic`
- [ ] Start command: `gunicorn core.wsgi`
- [ ] Health check URL: `/admin/` (проверить доступность)

---

## 🧪 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ

### Тест 1: Вход через Google (новый пользователь)
```
1. Открыть https://jobly.kz/accounts/login/
2. Кликнуть "Войти через Google"
3. Выбрать Google аккаунт (если не вошли в Google)
4. ✓ Успешный логин
5. ✓ Перенаправление на /
6. ✓ Пользователь авторизован (видна кнопка "Logout")
```

**Проверка в БД:**
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from allauth.socialaccount.models import SocialAccount
>>> user = User.objects.filter(email='your-test@gmail.com').first()
>>> print(user.first_name, user.last_name)  # Должны быть заполнены
>>> print(SocialAccount.objects.filter(user=user).first())  # Должен быть привязан
```

### Тест 2: Регистрация через Google (новый пользователь с другим email)
```
1. Открыть https://jobly.kz/accounts/signup/
2. Кликнуть "Зарегистрироваться через Google"
3. Выбрать другой Google аккаунт
4. ✓ Создается новый пользователь
5. ✓ Email заполняется автоматически
6. ✓ Пользователь авторизуется
```

### Тест 3: Вход через Google (существующий пользователь)
```
1. Создать пользователя: python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.create_user('testuser', 'test@gmail.com', 'pass123')
2. Открыть https://jobly.kz/accounts/login/
3. Кликнуть "Войти через Google" с email test@gmail.com
4. ✓ Социальный аккаунт связывается с существующим пользователем
5. ✓ Логин успешен
```

### Тест 4: Обычный вход (email + пароль)
```
1. Открыть https://jobly.kz/accounts/login/
2. Заполнить форму (username/email + пароль)
3. ✓ Логин успешен
4. ✓ Перенаправление на /
```

### Тест 5: Обычная регистрация
```
1. Открыть https://jobly.kz/accounts/signup/
2. Заполнить форму (email, username, пароль)
3. ✓ Аккаунт создан
4. ✓ Пользователь авторизуется
5. ✓ Перенаправление на /
```

### Тест 6: Восстановление пароля
```
1. Открыть https://jobly.kz/accounts/password/reset/
2. Заполнить email
3. ✓ Email отправлен (проверить в консоли или почте)
4. ✓ Ссылка в письме работает
5. ✓ Можно установить новый пароль
```

### Тест 7: Выход
```
1. Быть авторизованным пользователем
2. Кликнуть "Logout" (если видна кнопка) или открыть /accounts/logout/
3. ✓ Сессия завершается
4. ✓ Перенаправление на LOGIN_REDIRECT_URL
5. ✓ Кнопка "Logout" исчезает
```

### Тест 8: Mobile (мобильный телефон)
```
1. Открыть https://jobly.kz/accounts/login/ на мобильном
2. ✓ Шаблоны адаптивны (не обрезаны)
3. ✓ Кнопки нажимаются правильно
4. ✓ Формы заполняются без проблем
5. ✓ OAuth поток работает на мобильном
```

### Тест 9: Браузеры
- [ ] Chrome/Edge ✓
- [ ] Firefox ✓
- [ ] Safari ✓
- [ ] Safari на iOS ✓
- [ ] Chrome на Android ✓

---

## 🔍 ПРОВЕРКА БЕЗОПАСНОСТИ

- [ ] No secrets in logs: `grep -r "GOOGLE_OAUTH2" --include="*.py" classes-main/`
- [ ] No hardcoded credentials in settings.py
- [ ] CSRF protection включена: `{% csrf_token %}` в формах
- [ ] SQL injection невозможна (используется ORM Django)
- [ ] XSS защита (HTML автоматически экранируется в шаблонах)
- [ ] Rate limiting настроен (опционально)

---

## 📊 МОНИТОРИНГ

### Метрики для отслеживания
- [ ] Количество новых пользователей в неделю
- [ ] Процент успешных логинов через Google
- [ ] Процент отказов при входе
- [ ] Время ответа при входе (должно быть < 2 сек)
- [ ] Ошибки в логах (grep для `ERROR` или `EXCEPTION`)

### Команды для проверки
```bash
# Посчитать пользователей
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()

# Посчитать социальные аккаунты
>>> from allauth.socialaccount.models import SocialAccount
>>> SocialAccount.objects.count()

# Посчитать Google аккаунты
>>> SocialAccount.objects.filter(provider='google').count()
```

---

## 📝 ДОКУМЕНТАЦИЯ ДЛЯ КОМАНДЫ

**Файлы для документирования:**
- [ ] `ALLAUTH_SETUP.md` - основная инструкция
- [ ] `QUICK_REFERENCE_OAUTH.md` - быстрая справка
- [ ] `CSS_CUSTOMIZATION.md` - примеры CSS
- [ ] `ADAPTERS_READY_TO_USE.py` - готовый код адаптеров

**Обучение команды:**
- [ ] Все разработчики прочитали `QUICK_REFERENCE_OAUTH.md`
- [ ] DevOps настроил переменные окружения
- [ ] Support знает, где находятся логи

---

## 🚀 ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД ДЕПЛОЕМ

```bash
# 1. Проверить синтаксис
python manage.py check

# 2. Запустить миграции
python manage.py migrate

# 3. Собрать статические файлы
python manage.py collectstatic --noinput

# 4. Запустить тесты (если есть)
python manage.py test

# 5. Проверить шаблоны (убедиться они переопределены)
ls -la templates/allauth/account/login.html

# 6. Запустить локально один раз
python manage.py runserver

# 7. Проверить URLs
python manage.py shell
>>> from django.urls import reverse
>>> print(reverse('account_login'))
>>> print(reverse('socialaccount_login', args=['google']))

# 8. Проверить миграции и БД
python manage.py showmigrations
```

---

## ✅ ДЕПЛОЙ

```bash
# На Render.com (если используется)
git push render main

# На собственном сервере
git push origin main
ssh user@server.com
cd /path/to/project
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
supervisorctl restart jobly
```

---

**Дата проверки:** _______________  
**Проверил:** _______________  
**Статус:** ✅ ГОТОВО К ДЕПЛОЮ
