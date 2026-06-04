# 📊 ПРИМЕРЫ ВЫВОДА ТЕСТОВ И КОМАНД

---

## 🧪 ВЫВОД ТЕСТА ПРОИЗВОДИТЕЛЬНОСТИ

### Запуск:
```bash
pytest tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance -s -v
```

### Пример вывода:

```
tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance 

🧹 Кэш очищен

⏱️  Первый запрос (без кэша): 47.32 ms

⏱️  Второй запрос (с кэшем): 8.91 ms

📊 РЕЗУЛЬТАТЫ ТЕСТА HOME PAGE:
   Без кэша:    47.32 ms
   С кэшем:     8.91 ms
   Ускорение:   5.31x раз
   ✅ Тест PASSED (минимальное требование: 1.5x)

PASSED                                                                     [100%]
```

---

## 🔍 ВЫВОД ВСЕХ ТЕСТОВ ПРОИЗВОДИТЕЛЬНОСТИ

### Запуск:
```bash
pytest tests/performance/test_cache_performance.py -s -v
```

### Пример вывода:

```
tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance 

🧹 Кэш очищен

⏱️  Первый запрос (без кэша): 42.15 ms

⏱️  Второй запрос (с кэшем): 7.85 ms

📊 РЕЗУЛЬТАТЫ ТЕСТА HOME PAGE:
   Без кэша:    42.15 ms
   С кэшем:     7.85 ms
   Ускорение:   5.37x раз
   ✅ Тест PASSED (минимальное требование: 1.5x)

PASSED                                                                     [ 16%]

tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_consistency 

🧹 Кэш очищен

⏱️  Запрос #1: 41.23 ms

⏱️  Запрос #2: 8.12 ms

⏱️  Запрос #3: 7.56 ms

📊 РЕЗУЛЬТАТЫ ТЕСТА CONSISTENCY:
   Запрос 1: 41.23 ms (без кэша)
   Запрос 2: 8.12 ms (с кэшем)
   Запрос 3: 7.56 ms (с кэшем)
   ✅ Все ответы идентичны

PASSED                                                                     [ 33%]

tests/performance/test_cache_performance.py::TestSearchPagePerformance::test_search_page_cache_improves_performance 

🧹 Кэш очищен

⏱️  Поиск без кэша: 35.67 ms

⏱️  Поиск с кэшем (тот же запрос): 6.34 ms

📊 РЕЗУЛЬТАТЫ ТЕСТА SEARCH PAGE:
   Без кэша:    35.67 ms
   С кэшем:     6.34 ms
   Ускорение:   5.63x раз
   ✅ Тест PASSED (минимальное требование: 1.5x)

PASSED                                                                     [ 50%]

tests/performance/test_cache_performance.py::TestApplicationPerformance::test_multiple_pages_with_and_without_cache 

======================================================================
📊 КОМПЛЕКСНЫЙ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПРИЛОЖЕНИЯ
======================================================================

🧹 Кэш очищен

⏱️  [HOME] Первый запрос (без кэша): 42.34 ms

⏱️  [HOME] Второй запрос (с кэшем): 8.01 ms

🧹 Кэш очищен

⏱️  [SEARCH] Первый запрос (без кэша): 38.92 ms

⏱️  [SEARCH] Второй запрос (с кэшем): 7.12 ms

======================================================================
Страница             Без кэша        С кэшем         Ускорение      
------================================================================
home                 42.34ms         8.01ms          5.29x         
search               38.92ms         7.12ms          5.47x         
======================================================================

PASSED                                                                     [ 66%]

tests/performance/test_cache_performance.py::test_cache_clear_invalidates_cache 

======================================================================
🧹 ТЕСТ ОЧИСТКИ КЭША
======================================================================

🧹 Кэш очищен

⏱️  Запрос 1 (без кэша): 41.56 ms

⏱️  Запрос 2 (с кэшем): 7.89 ms

🧹 Кэш очищен

⏱️  Запрос 3 (после очистки): 40.12 ms

⏱️  Запрос 4 (снова с кэшем): 8.34 ms

📊 РЕЗУЛЬТАТЫ:
   1️⃣  Без кэша:          41.56 ms
   2️⃣  С кэшем:           7.89 ms (быстрее в 5.27x)
   3️⃣  После очистки:     40.12 ms (снова медленнее)
   4️⃣  С кэшем снова:     8.34 ms (снова быстро)
   ✅ Кэш корректно очищается и переиспользуется

PASSED                                                                     [ 83%]

tests/performance/test_cache_performance.py::test_cache_with_rapid_requests 

======================================================================
⚡ ТЕСТ ЧАСТЫХ ЗАПРОСОВ
======================================================================

🧹 Кэш очищен

⏱️  Запрос 1: 42.01 ms

⏱️  Запрос 2: 7.56 ms

⏱️  Запрос 3: 7.23 ms

⏱️  Запрос 4: 7.45 ms

⏱️  Запрос 5: 7.34 ms

⏱️  Запрос 6: 7.67 ms

⏱️  Запрос 7: 7.89 ms

⏱️  Запрос 8: 7.45 ms

⏱️  Запрос 9: 7.56 ms

⏱️  Запрос 10: 7.23 ms

📊 РЕЗУЛЬТАТЫ:
   1-й запрос (без кэша):  42.01 ms
   Средний (с кэшем):      7.57 ms
   Ускорение:              5.55x
   Min время (с кэшем):    7.23 ms
   Max время (с кэшем):    7.89 ms

PASSED                                                                     [100%]

======================================================================
7 passed in 2.45s
======================================================================
```

---

## 🔐 ВЫВОД КОМАНДЫ test-redis

### Запуск:
```bash
python manage_cache.py test-redis
```

### Пример вывода (успешно):

```
🔍 ТЕСТИРОВАНИЕ REDIS:

URL: redis://localhost:6379/0
✅ Подключение успешно!
✅ Запись/чтение работает
✅ Удаление ключей работает
```

### Пример вывода (ошибка):

```
🔍 ТЕСТИРОВАНИЕ REDIS:

URL: redis://localhost:6379/0
❌ Redis не доступен: ConnectionRefusedError - [Errno 111] Connection refused
   Убедитесь, что Redis запущен и доступен по адресу redis://localhost:6379/0
```

---

## 📊 ВЫВОД КОМАНДЫ stats

### Запуск:
```bash
python manage_cache.py stats
```

### Пример вывода (Redis):

```
📊 ИНФОРМАЦИЯ О КЭШЕ:

Backend: django.core.cache.backends.redis.RedisCache
Location: redis://localhost:6379/0

Redis статистика:
  - Connected: ✅
  - Memory used: 2.34M
  - Number of keys: 47
  - Version: 7.0.5

📍 Примеры ключей кэша:
   - home_page_html (293s)
   - search_python (600s)
   - search_javascript (599s)
   - user_profile:42 (3600s)
   - job_list:page1 (1800s)
   - cache_key_temp (no expiry)
```

### Пример вывода (LocMemCache):

```
📊 ИНФОРМАЦИЯ О КЭШЕ:

Backend: django.core.cache.backends.locmem.LocMemCache
Location: Local Memory (LocMemCache)
⚠️  Local memory cache потеряется при перезагрузке приложения
```

---

## 🔄 ВЫВОД МИГРАЦИЙ

### Запуск:
```bash
python manage.py migrate
```

### Пример вывода:

```
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, learning, sessions

Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying accounts.0002_add_profile... OK
  Applying accounts.0003_add_role_field... OK
  Applying learning.0001_initial... OK
  Applying learning.0002_add_video... OK
  Applying sessions.0001_initial... OK
```

---

## 🤖 ВЫВОД GITHUB ACTIONS (CI/CD)

### Лог в GitHub Actions:

```
Run migrations
django/workflows/deploy.yml:27: Running Django migrations
python manage.py migrate --noinput

Operations to perform:
  Apply all migrations: accounts, auth, contenttypes, learning, sessions

Running migrations:
  Applying accounts.0001_initial... OK
  Applying accounts.0002_add_profile... OK
  Applying learning.0001_initial... OK

Run Alembic migrations (if applicable)
python -m alembic upgrade head

INFO  [alembic.runtime.migration] Context impl PostgresqlImpl with target metadata
INFO  [alembic.runtime.migration] Will assume transactional DDL per dialect.
✅ All migrations are up to date!

Run tests
pytest -v

tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance PASSED
tests/performance/test_cache_performance.py::TestSearchPagePerformance::test_search_page_cache_improves_performance PASSED
tests/unit/ PASSED
tests/integration/ PASSED

✅ All tests passed!
```

---

## 🚀 ВЫВОД RENDER PRE-DEPLOY

### Лог в Render Dashboard при деплое:

```
=== Build started ===

Installing dependencies
Collecting requirements...
pip install -r requirements.txt
Successfully installed Django, redis, pytest, ...

=== Pre-deploy command started ===

Running: cd classes-main && python manage.py migrate --noinput

Operations to perform:
  Apply all migrations: accounts, auth, contenttypes, learning

Running migrations:
  Applying accounts.0001_initial... OK
  Applying learning.0001_initial... OK
  ...

✅ Pre-deploy миграции завершены успешно!

=== Starting service ===

Gunicorn listening on [::]:10000
✅ Service started successfully!
```

---

## ⚠️ ПРИМЕРЫ ОШИБОК И РЕШЕНИЙ

### Ошибка 1: Redis не подключен

```bash
$ pytest tests/performance/test_cache_performance.py -s

ERROR - Redis connection refused
```

**Решение:**
```bash
# Убедитесь, что Redis запущен
redis-server

# Или проверьте в Docker
docker ps | grep redis

# Проверьте REDIS_URL в settings.py
python manage_cache.py test-redis
```

---

### Ошибка 2: Миграции не применены

```bash
$ python manage.py migrate

Error: no such table: accounts_profile
```

**Решение:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Ошибка 3: Тест падает с assert

```bash
$ pytest tests/performance/test_cache_performance.py -s

AssertionError: Кэш не дал ожидаемое улучшение. 
Ускорение: 1.1x, ожидалось минимум 1.5x.
```

**Решение:**
- Проверьте, что Redis работает
- Проверьте, что view кэширует результаты
- Увеличьте timeout теста (если сервер медленный)

---

## 📈 ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ

| Ускорение | Оценка | Действие |
|-----------|--------|---------|
| > 10x | 🌟 Отлично | Кэш очень эффективен |
| 5-10x | ✅ Хорошо | Нормально работает |
| 1.5-5x | ✓ Приемлемо | Минимум требований |
| 1-1.5x | ⚠️ Плохо | Нужно отладить |
| < 1x | ❌ Ошибка | Кэш не работает |
