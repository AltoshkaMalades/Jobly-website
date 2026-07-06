# Launch Readiness Checklist - Функции и их реализация

Полный справочник всех функций из Launch Readiness Checklist с описанием, назначением и местоположением.

---

## Infrastructure 🏗️

### 1. Domain live + HTTPS (padlock visible)
- **Что делает**: Обеспечивает защищённое соединение по HTTPS и видимый padlock в браузере
- **Где находится**: конфигурация сервера / nginx
- **Статус**: ✅ Требует настройки SSL сертификата на боевом сервере
- **Проверка**: 
  ```bash
  curl -I https://yourdomain.com  # Должен вернуть 200
  ```

### 2. CI/CD deploys on push to main
- **Что делает**: Автоматический деплой приложения при push в ветку main
- **Где находится**: `.github/workflows/` или `deploy.sh` → [classes-main/deploy.sh](classes-main/deploy.sh)
- **Как работает**:
  - Слушает события push в основную ветку
  - Запускает тесты
  - Если всё ок, разворачивает приложение на production сервере
- **Проверка**: Посмотреть статус в Actions на GitHub

### 3. Docker restart: unless-stopped
- **Что делает**: Контейнеры Docker автоматически перезагружаются после сбоя или перезагрузки сервера
- **Где находится**: [classes-main/docker-compose.yml](classes-main/docker-compose.yml) → параметр `restart_policy`
- **Конфиг**:
  ```yaml
  restart_policy:
    condition: unless-stopped
  ```
- **Проверка**: `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Restart}}"`

### 4. DB backup running daily (cron)
- **Что делает**: Автоматическое ежедневное резервное копирование базы данных в 02:00
- **Где находится**:
  - Скрипт бэкапа: [classes-main/backup.sh](classes-main/backup.sh)
  - Скрипт запуска для Windows: [classes-main/scripts/run_backup_task.ps1](classes-main/scripts/run_backup_task.ps1)
  - Установщик задачи: [classes-main/scripts/install_backup_task.ps1](classes-main/scripts/install_backup_task.ps1)
  - Пример cron: [classes-main/cron/backup.cron](classes-main/cron/backup.cron)
- **Как работает**:
  ```bash
  # Linux/macOS: использует crontab
  0 2 * * * /bin/bash /path/to/backup.sh
  
  # Windows: использует Task Scheduler
  schtasks /Create /TN SimulatorBackup /SC DAILY /ST 02:00
  ```
- **Параметры**:
  - `BACKUP_DIR`: папка для хранения бэкапов (default: `backups/`)
  - `RETENTION_DAYS`: дни хранения старых бэкапов (default: 7)
  - `DATABASE_URL`: URL подключения к БД (из переменной окружения)
- **Проверка**:
  ```bash
  ls -lh backups/  # Должны быть файлы формата backup_YYYY-MM-DD_HH-MM.sql
  ```

---

## Security 🔒

### 1. No secrets in git (trufflehog clean)
- **Что делает**: Сканирует репозиторий на наличие скрытых ключей, токенов и других секретов
- **Где находится**: [classes-main/scan_secrets.py](classes-main/scan_secrets.py)
- **Как использовать**:
  ```bash
  python scan_secrets.py
  ```
- **Проверяет**:
  - `.env` файлы (должны быть в `.gitignore`)
  - API ключи в коде
  - Приватные ключи
  - Токены доступа
  - Credentials в строках подключения БД
- **Проверка**: Должен вернуть 0 найденных секретов в git

### 2. DEBUG=false in production
- **Что делает**: Отключает режим отладки Django для предотвращения утечки информации
- **Где находится**: [classes-main/core/settings.py](classes-main/core/settings.py) → переменная `DEBUG`
- **Как задать**:
  ```python
  DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
  # На production: не устанавливать DEBUG или DEBUG=False
  ```
- **Почему критично**: Когда `DEBUG=True`, Django показывает полные traceback с переменными окружения и путями файлов

### 3. Security headers B+ on securityheaders.com
- **Что делает**: Устанавливает набор HTTP заголовков для защиты от распространённых веб-атак
- **Где находится**: [classes-main/core/middleware.py](classes-main/core/middleware.py) → класс `SecurityHeadersMiddleware`
- **Какие заголовки устанавливаются**:
  ```python
  X-Content-Type-Options: nosniff          # Предотвращает MIME sniffing
  X-Frame-Options: DENY                    # Защита от clickjacking (DENY/SAMEORIGIN)
  X-XSS-Protection: 1; mode=block          # Защита от XSS
  Strict-Transport-Security: max-age=...   # Принудительный HTTPS
  Content-Security-Policy: ...             # Контроль источников контента
  Permissions-Policy: ...                  # Контроль доступа браузера к функциям
  ```
- **Проверка заголовков**:
  ```bash
  python test_security_headers.py
  ```
  Или на https://securityheaders.com

### 4. RBAC: admin endpoints protected (403 test)
- **Что делает**: Защищает админ-панель и API endpoints от несанкционированного доступа
- **Где находится**: 
  - Django Admin: встроенная защита [classes-main/accounts/models.py](classes-main/accounts/models.py)
  - Custom RBAC: [classes-main/accounts/decorators.py](classes-main/accounts/decorators.py)
- **Как работает**:
  ```python
  # Требует аутентификацию
  @login_required
  def admin_view(request):
      pass
  
  # Требует определённые роли
  @require_permission('admin')
  def protected_endpoint(request):
      pass
  ```
- **Проверка**: 
  ```bash
  # Без авторизации должен вернуть 403 Forbidden
  curl https://api.example.com/admin/ 
  
  # С авторизацией и нужной ролью должен вернуть 200
  curl -H "Authorization: Bearer TOKEN" https://api.example.com/admin/
  ```

---

## Payments 💳

### 1. Bereke callback URL is production (not ngrok)
- **Что делает**: Webhooks от Bereke Payment System приходят на реальный production URL, а не на локальный
- **Где находится**: [classes-main/payments/views.py](classes-main/payments/views.py) → функция `payment_webhook_bereke`
- **Настройка в Bereke Dashboard**:
  ```
  Webhook URL: https://yourdomain.com/api/payments/bereke/callback/
  ```
- **Проверка**: `curl https://yourdomain.com/api/payments/bereke/callback/`

### 2. Test payment end-to-end on prod server
- **Что делает**: Проверяет полный цикл платежа: создание → редирект → callback → обновление статуса
- **Где находится**: 
  - API endpoint: [classes-main/payments/views.py](classes-main/payments/views.py) → функция `create_payment`
  - Тесты: [classes-main/tests/integration/payments/](classes-main/tests/integration/payments/)
- **Как протестировать**:
  ```bash
  # 1. Запустить тесты
  python manage.py test tests.integration.payments
  
  # 2. Вручную через API
  curl -X POST https://api.example.com/api/payments/create/ \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "amount": 10000,
      "currency": "KZT",
      "provider": "bereke",
      "description": "Test payment"
    }'
  ```

### 3. Failed payment → order status 'failed'
- **Что делает**: Автоматически переводит заказ в статус "failed" при отклонении платежа
- **Где находится**: 
  - Модель: [classes-main/payments/models.py](classes-main/payments/models.py)
  - Сервис: [classes-main/payments/services/service.py](classes-main/payments/services/service.py)
  - Обработка webhook: [classes-main/payments/views.py](classes-main/payments/views.py) → `payment_webhook_bereke`
- **Как работает**:
  ```python
  # При приёме callback от платежной системы
  if callback_status == 'REJECTED':
      order.status = 'failed'
      order.save()
  ```
- **Проверка**: 
  ```bash
  # Запустить отклоняемый платеж
  # Проверить статус заказа
  curl https://api.example.com/orders/{order_id}/ -H "Authorization: Bearer TOKEN"
  ```

### 4. Refund endpoint working (admin only)
- **Что делает**: API endpoint для возврата средств, доступный только администраторам
- **Где находится**: [classes-main/payments/views.py](classes-main/payments/views.py) → функция `refund_payment`
- **Endpoint**:
  ```
  POST /api/payments/refund/{transaction_id}/
  ```
- **Требования**:
  - Пользователь должен быть администратором
  - Платеж должен быть в статусе 'paid'
- **Проверка**:
  ```bash
  # Без прав доступа
  curl -X POST https://api.example.com/api/payments/refund/txn123/
  # → 403 Forbidden
  
  # С правами администратора
  curl -X POST https://api.example.com/api/payments/refund/txn123/ \
    -H "Authorization: Bearer ADMIN_TOKEN"
  # → 200 OK, возврат обработан
  ```

---

## Observability 📊

### 1. Prometheus /metrics endpoint live
- **Что делает**: Собирает метрики приложения в формате Prometheus для мониторинга
- **Где находится**:
  - Метрики: [classes-main/core/metrics.py](classes-main/core/metrics.py)
  - Middleware: [classes-main/core/middleware_metrics.py](classes-main/core/middleware_metrics.py)
  - Endpoint: [classes-main/core/urls_metrics.py](classes-main/core/urls_metrics.py)
- **Какие метрики собираются**:
  ```
  simulator_http_requests_total          # Всего HTTP запросов
  simulator_http_request_duration_seconds # Время ответа (histogram)
  simulator_http_request_exceptions_total # Ошибки и исключения
  ```
- **Проверка**:
  ```bash
  curl http://localhost:8000/metrics/
  # Должен вернуть Prometheus текст формат
  ```

### 2. Grafana dashboard showing 4+ golden signals
- **Что делает**: Визуализирует ключевые метрики приложения: latency, traffic, errors, saturation
- **Где находится**:
  - Dashboard конфиг: [classes-main/grafana/dashboards/](classes-main/grafana/dashboards/)
  - Provisioning: [classes-main/grafana/provisioning/](classes-main/grafana/provisioning/)
- **Золотые сигналы** (4 метрики SRE):
  1. **Latency** - время ответа (p50, p95, p99)
  2. **Traffic** - количество запросов в секунду
  3. **Errors** - процент ошибок (4xx, 5xx)
  4. **Saturation** - использование ресурсов (CPU, memory, DB connections)
- **Доступ**: `http://grafana.example.com:3000`
- **Проверка**: Панель должна показывать график одного из параметров в реальном времени

### 3. At least 2 alerts configured (error rate + downtime)
- **Что делает**: Автоматические оповещения о проблемах: высокий уровень ошибок или недоступность сервиса
- **Где находится**: [classes-main/prometheus/alert_rules.yml](classes-main/prometheus/alert_rules.yml)
- **Примеры алертов**:
  ```yaml
  # Alert 1: High Error Rate
  - alert: HighErrorRate
    expr: rate(simulator_http_request_exceptions_total[5m]) > 0.05
    annotations:
      summary: "High error rate detected"
  
  # Alert 2: Service Down
  - alert: ServiceDown
    expr: up{job="simulator"} == 0
    annotations:
      summary: "Application is down"
  ```
- **Проверка**: Алерты должны отправляться в Slack / Email при срабатывании

### 4. PostHog: 10+ events + funnel visible
- **Что делает**: Отслеживает поведение пользователей: события, воронки конверсии, когорты
- **Где находится**: [classes-main/core/posthog.py](classes-main/core/posthog.py)
- **Какие события отслеживаются**:
  ```python
  'checkout_started'      # Пользователь начал оформление
  'payment_completed'     # Платёж успешно завершён
  'payment_failed'        # Платёж отклонён
  'course_enrolled'       # Пользователь записался на курс
  'subscription_created'  # Подписка активирована
  'login'                 # Вход в систему
  'signup'                # Регистрация
  'page_view'             # Просмотр страницы
  ```
- **Воронка конверсии** (Funnel): signup → checkout_started → payment_completed
- **Проверка**: 
  ```bash
  # На posthog.com должны быть видны события
  # Воронка должна показывать: 100% signup → 40% checkout → 30% payment
  ```

---

## Performance ⚡

### 1. Locust: 50+ users, failure < 1%
- **Что делает**: Load testing - проверяет приложение на способность выдержать нагрузку 50+ одновременных пользователей
- **Где находится**: [classes-main/locustfile.py](classes-main/locustfile.py)
- **Как запустить**:
  ```bash
  # Консоль локуста
  locust -f locustfile.py -u 50 -r 5 --host http://localhost:8000
  
  # Затем открыть http://localhost:8089
  # Запустить нагрузочный тест
  ```
- **Какие сценарии тестируются**:
  - Загрузка главной страницы
  - Поиск товаров
  - Оформление платежа
  - Просмотр профиля
- **Критерии успеха**:
  - Failure rate < 1%
  - p95 latency < 500ms
  - p99 latency < 1000ms

### 2. p95 latency < 500ms under load
- **Что делает**: Измеряет время ответа: 95% запросов должны ответить быстрее 500мс
- **Где собирается**: Prometheus метрика `simulator_http_request_duration_seconds`
- **Как проверить**:
  ```bash
  # В Grafana смотреть график latency
  # Или запрос к Prometheus:
  histogram_quantile(0.95, simulator_http_request_duration_seconds)
  ```
- **Если медленнее**:
  - Оптимизировать SQL запросы (check N+1)
  - Добавить кэширование
  - Масштабировать горизонтально

### 3. N+1 queries fixed, indexes on key columns
- **Что делает**: Оптимизирует БД запросы: предотвращает множество малых запросов вместо одного, добавляет индексы
- **Где находится**: 
  - ORM оптимизация: [classes-main/payments/models.py](classes-main/payments/models.py)
  - Индексы в миграциях: [classes-main/payments/migrations/](classes-main/payments/migrations/)
- **Как исправить N+1**:
  ```python
  # ❌ Плохо: N+1 запрос
  orders = Order.objects.all()
  for order in orders:
      print(order.user.name)  # Один запрос на каждый заказ!
  
  # ✅ Хорошо: select_related
  orders = Order.objects.select_related('user').all()
  for order in orders:
      print(order.user.name)  # Всё в одном запросе
  ```
- **Как добавить индексы**:
  ```python
  # В модели
  class Order(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
      status = models.CharField(max_length=20, db_index=True)
  ```
- **Проверка**: 
  ```bash
  # Включить логирование SQL
  python manage.py shell
  >>> from django.db import reset_queries, connection
  >>> reset_queries()
  >>> # выполнить операцию
  >>> len(connection.queries)  # Должно быть минимум
  ```

### 4. Redis cache on high-traffic endpoints
- **Что делает**: Кэширует результаты часто запрашиваемых эндпойнтов в Redis
- **Где находится**: 
  - Конфиг кэша: [classes-main/core/settings.py](classes-main/core/settings.py) → `CACHES`
  - Использование: [classes-main/learning/views.py](classes-main/learning/views.py)
  - Управление: [classes-main/manage_cache.py](classes-main/manage_cache.py)
- **Какие эндпойнты кэшируются**:
  ```python
  @cache_page(60 * 15)  # Кэш на 15 минут
  def course_list(request):
      return render(request, 'courses.html', {'courses': Course.objects.all()})
  ```
- **Команды управления**:
  ```bash
  # Очистить весь кэш
  python manage_cache.py clear
  
  # Получить статистику
  python manage_cache.py stats
  
  # Тест подключения Redis
  python manage_cache.py test_redis
  ```
- **Проверка**:
  ```bash
  redis-cli PING  # Должен вернуть PONG
  ```

---

## Operations 🚀

### 1. Runbook written for 3+ scenarios in Confluence
- **Что делает**: Документирует процедуры: восстановление БД, откат релиза, миграция данных
- **Где находится**: Confluence (вне репо) или документ в [MONITORING_DASHBOARD_README.md](classes-main/MONITORING_DASHBOARD_README.md)
- **Сценарии**:
  1. **Database Restore**: восстановление из бэкапа при сбое БД
  2. **Rollback**: откат на предыдущую версию при критической ошибке
  3. **Data Migration**: миграция данных при обновлении схемы БД
  4. **Incident Response**: действия при высокой нагрузке или DDoS
  5. **Payment System Failure**: fallback если Bereke недоступна
- **Требование**: Каждый runbook должен содержать step-by-step инструкции

### 2. Health check returns DB + cache status
- **Что делает**: Endpoint который проверяет здоровье всех критических компонентов системы
- **Где находится**: [classes-main/core/views.py](classes-main/core/views.py) → функция `health_check`
- **Endpoint**:
  ```
  GET /health/
  ```
- **Response**:
  ```json
  {
    "status": "ok",
    "database": "ok",
    "cache": "ok",
    "database_error": null,
    "cache_error": null
  }
  ```
- **HTTP коды**:
  - 200 OK - всё работает
  - 500 Internal Server Error - что-то сломалось
- **Проверка**: 
  ```bash
  curl http://localhost:8000/health/
  # Загрузить балансер должен перенаправлять трафик на основной сервер
  ```

### 3. Team can SSH to server and restart app
- **Что делает**: Команда разработчиков может подключиться к production серверу и перезагрузить приложение
- **Где находится**: процесс доступа через bastion host и SSH keys
- **Как работает**:
  ```bash
  # Команда имеет доступ к приватному ключу
  ssh -i ~/.ssh/prod_key user@prod-server.com
  
  # После входа
  cd /app && docker-compose restart web
  ```
- **Требование**: Доступ должен быть логирован и ограничен по ролям

### 4. All Jira tickets: Done, Confluence up to date
- **Что делает**: Все задачи перед запуском помечены как завершённые, документация синхронизирована
- **Где находится**: Jira (вне репо) и Confluence
- **Проверка**:
  - ✅ Все задачи спринта в статусе Done
  - ✅ Confluence содержит актуальную документацию
  - ✅ README в репо актуален
- **Документация должна содержать**:
  - Архитектуру системы
  - API документацию
  - Процессы развёртывания
  - Процедуры восстановления

---

## Дополнительные утилиты

### Backup script
**Файл**: [classes-main/backup.sh](classes-main/backup.sh)

```bash
# Ручное создание бэкапа
./backup.sh

# С кастомными переменными
BACKUP_DIR=/mnt/backup RETENTION_DAYS=30 ./backup.sh
```

**Параметры окружения**:
- `DATABASE_URL` - строка подключения к PostgreSQL
- `BACKUP_DIR` - папка для сохранения (default: `backups/`)
- `RETENTION_DAYS` - дни хранения (default: 7)

### Cache management
**Файл**: [classes-main/manage_cache.py](classes-main/manage_cache.py)

```bash
# Очистить кэш
python manage_cache.py clear

# Статистика кэша
python manage_cache.py stats

# Тест Redis подключения
python manage_cache.py test_redis
```

### Secret scanning
**Файл**: [classes-main/scan_secrets.py](classes-main/scan_secrets.py)

```bash
# Сканировать репозиторий на секреты
python scan_secrets.py
```

---

## Summary Таблица 

| Область | Функция | Файл | Статус |
|---------|---------|------|--------|
| Infrastructure | Domain + HTTPS | - | ❌ Нужна настройка SSL |
| Infrastructure | CI/CD | deploy.sh | ✅ Готово |
| Infrastructure | Docker restart | docker-compose.yml | ✅ Готово |
| Infrastructure | DB backup | backup.sh, scripts/ | ✅ Готово |
| Security | No secrets | scan_secrets.py | ✅ Готово |
| Security | DEBUG=false | core/settings.py | ✅ Готово |
| Security | Security headers | core/middleware.py | ✅ Готово |
| Security | RBAC | accounts/decorators.py | ✅ Готово |
| Payments | Bereke callback | payments/views.py | ✅ Готово |
| Payments | Test payment | tests/integration/payments/ | ✅ Готово |
| Payments | Failed payment | payments/models.py | ✅ Готово |
| Payments | Refund endpoint | payments/views.py | ✅ Готово |
| Observability | Prometheus metrics | core/metrics.py | ✅ Готово |
| Observability | Grafana dashboard | grafana/dashboards/ | ✅ Готово |
| Observability | Alerts | prometheus/alert_rules.yml | ✅ Готово |
| Observability | PostHog events | core/posthog.py | ✅ Готово |
| Performance | Locust load test | locustfile.py | ✅ Готово |
| Performance | Latency p95 | core/metrics.py | ✅ Готово |
| Performance | N+1 fixed | payments/models.py | ✅ Готово |
| Performance | Redis cache | learning/views.py | ✅ Готово |
| Operations | Runbook | MONITORING_DASHBOARD_README.md | ⚠️ Требует расширения |
| Operations | Health check | core/views.py | ✅ Готово |
| Operations | SSH access | - | ⚠️ Нужна настройка доступа |
| Operations | Jira tickets | - | ⚠️ Внешняя система |

---

## Подготовка к запуску (Final Checklist)

- [ ] Все функции Infrastructure настроены
- [ ] Все Security функции в production режиме
- [ ] Все платежи прошли E2E тестирование
- [ ] Observability полностью интегрирована
- [ ] Performance тесты пройдены успешно
- [ ] Operations процессы документированы
- [ ] Team обучена процедурам
- [ ] Backup запущен и логируется
- [ ] Мониторинг активен и отправляет алерты
- [ ] Все Jira tickets в Done
- [ ] Confluence документация актуальна
- [ ] ✅ **Готово к запуску на Production!**
