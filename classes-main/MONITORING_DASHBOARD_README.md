# 📊 Monitoring Dashboard

Единая страница со всеми новыми функциями мониторинга и наблюдаемости.

## 🚀 Доступ

```
http://localhost:8000/api/monitoring/
```

или

```
http://your-domain.com/api/monitoring/
```

## 📋 Что включено

### 1. **Основные метрики** (Real-time)
- 📈 **Request Rate** - количество запросов в минуту
- ⏱️ **Latency (avg)** - средняя латентность в миллисекундах
  - p50, p95, p99 процентили
- ❌ **Errors** - количество ошибок за последние 5 минут
- 🔧 **System Health** - статус всех компонентов

### 2. **Быстрые ссылки** на другие инструменты
- 📊 Prometheus (http://localhost:9090)
- 📈 Grafana (http://localhost:3000)
- ⚡ Locust Load Test (http://localhost:8089)
- 📡 Raw Metrics endpoint (/metrics/)

### 3. **Recent Logs** (JSON логи)
- Последние 20 логов из `debug.json.log`
- Структурированный формат с:
  - `timestamp` - время события
  - `level` - уровень логирования (INFO, ERROR, WARNING)
  - `logger` - модуль логирования
  - `message` - сообщение
  - `request_id` - ID запроса для трейсинга
  - `user` - пользователь
  - `path` - путь запроса
  - `method` - HTTP метод

### 4. **API Endpoints**

#### `GET /api/monitoring/`
Основная страница с HTML интерфейсом

#### `GET /api/monitoring/api/metrics/`
JSON с текущими метриками
```json
{
  "timestamp": "2026-06-29T12:34:56.789000",
  "services": {
    "database": "up",
    "redis": "up"
  },
  "metrics": {
    "total_requests": 1234,
    "request_duration_avg": 0.042,
    "request_exceptions": 3
  },
  "endpoints": {
    "GET /health/": {
      "total": 500,
      "by_status": {"200": 500}
    }
  }
}
```

#### `GET /api/monitoring/api/health/`
JSON со статусом всех сервисов
```json
{
  "timestamp": "2026-06-29T12:34:56.789000",
  "overall_status": "healthy",
  "services": {
    "django": {"status": "up", "url": "http://localhost:8000"},
    "prometheus": {"status": "up", "url": "http://localhost:9090"},
    "grafana": {"status": "up", "url": "http://localhost:3000"}
  }
}
```

#### `GET /api/monitoring/api/logs/`
JSON с последними логами
```json
{
  "logs": [
    {
      "timestamp": "2026-06-29 12:34:56",
      "level": "INFO",
      "logger": "django.server",
      "message": "GET /health/ 200 OK",
      "request_id": "abc-123-def",
      "user": "john",
      "path": "/health/",
      "method": "GET"
    }
  ]
}
```

## 🎨 Возможности

- ✅ **Real-time updates** - данные обновляются каждые 30 секунд
- ✅ **Responsive design** - работает на мобильных устройствах
- ✅ **Service health checks** - проверка доступности всех сервисов
- ✅ **Status indicators** - визуальные индикаторы статуса
- ✅ **Auto-refresh** - автоматическое обновление без перезагрузки страницы
- ✅ **Manual refresh** - кнопка для ручного обновления логов

## 📖 Использование

### Локально
```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
python manage.py runserver

# Открыть в браузере
http://localhost:8000/api/monitoring/
```

### Docker Compose
```bash
# Запустить все сервисы
docker-compose up -d

# Открыть в браузере
http://localhost:8000/api/monitoring/
```

### На production сервере
```bash
# Открыть в браузере
https://your-domain.com/api/monitoring/
```

## 🔍 Проверка функциональности

### 1. Проверить метрики обновляются
```bash
curl http://localhost:8000/api/monitoring/api/metrics/
# Должны быть ненулевые значения в metrics
```

### 2. Проверить здоровье сервисов
```bash
curl http://localhost:8000/api/monitoring/api/health/
# Должны быть статусы up/down для каждого сервиса
```

### 3. Проверить логи
```bash
curl http://localhost:8000/api/monitoring/api/logs/
# Должны быть последние 20 логов
```

### 4. Генерировать трафик
```bash
# Создать запросы для обновления метрик
for i in {1..100}; do 
  curl http://localhost:8000/health/ 
done

# Открыть http://localhost:8000/api/monitoring/
# Должны обновиться графики и метрики
```

## 🛠️ Настройка

### Изменить интервал обновления
В `templates/monitoring_dashboard.html` найти:
```javascript
const REFRESH_INTERVAL = 30000; // 30 seconds
```
И изменить на нужное значение в миллисекундах.

### Добавить новые метрики
В `core/views_monitoring_dashboard.py` функция `api_metrics_summary()` - добавить новые метрики в `metrics_data['metrics']`.

### Изменить вид графиков
В `templates/monitoring_dashboard.html` есть комментарии `// Charts Container` - там можно добавить Chart.js графики.

## 🚨 Проблемы

### Метрики не обновляются
1. Проверить что middleware включен в `settings.py`
2. Проверить что нет ошибок в логах: `docker logs simulator-web`

### Logs не показываются
1. Проверить что файл `debug.json.log` существует: `ls -la classes-main/debug.json.log`
2. Проверить что логирование включено в `settings.py`

### Сервисы показывают "down"
1. Проверить что все контейнеры запущены: `docker-compose ps`
2. Проверить сетевую доступность: `curl http://localhost:9090/-/healthy`

## 📚 Связанные документы

- [OPERATIONS_RUNBOOK.md](../OPERATIONS_RUNBOOK.md) - процедуры при инцидентах
- [LAUNCH_READINESS_CHECKLIST.md](../LAUNCH_READINESS_CHECKLIST.md) - чек-лист перед запуском
- [prometheus/alert_rules.yml](../prometheus/alert_rules.yml) - правила алертов
- [docker-compose.yml](../docker-compose.yml) - конфигурация сервисов

## 🔗 Интеграция с другими системами

### Prometheus
Метрики собираются из `/metrics/` endpoint и хранятся в Prometheus базе.

### Grafana
Использует Prometheus как источник данных и показывает graphql с 4 golden signals.

### Locust
Может быть запущен для генерации нагрузки: http://localhost:8089

## 📊 Метрики которые собираются

- `simulator_http_requests_total` - общее количество запросов
- `simulator_http_request_duration_seconds` - время обработки запроса (гистограмма)
- `simulator_http_request_exceptions` - количество исключений

Все метрики имеют labels:
- `method` - HTTP метод (GET, POST, etc.)
- `endpoint` - URL endpoint
- `status` - HTTP статус код (200, 404, 500, etc.)

## 🎯 Примеры использования

### Проверить Request Rate в Prometheus
```
rate(simulator_http_requests_total[5m])
```

### Проверить средний Response Time
```
rate(simulator_http_request_duration_seconds_sum[5m]) / rate(simulator_http_request_duration_seconds_count[5m])
```

### Проверить Error Rate
```
rate(simulator_http_request_duration_seconds_total[5m]{status=~"5.."}
```
