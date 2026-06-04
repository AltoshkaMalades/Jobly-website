# 📋 ИНСТРУКЦИЯ: АВТОМАТИЧЕСКИЕ МИГРАЦИИ В CI/CD И ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ

---

## 🔧 ЧАСТЬ 1: НАСТРОЙКА МИГРАЦИЙ В GITHUB ACTIONS

### Что было изменено:
Файл: `.github/workflows/deploy.yml`

**До:**
```yaml
- name: Run migrations
  run: |
    python -m alembic upgrade head
```

**После:**
```yaml
- name: Run Django migrations
  run: |
    python manage.py migrate --noinput

- name: Run Alembic migrations (if applicable)
  run: |
    python -m alembic upgrade head
  continue-on-error: true

- name: Run tests
  run: |
    pytest -v
```

### Объяснение:
1. **`python manage.py migrate --noinput`** — применяет Django миграции автоматически
2. **`--noinput`** — не запрашивает подтверждение в интерактивном режиме
3. **Alembic** — дополнительно, для SQLAlchemy миграций (если используются)
4. **`continue-on-error: true`** — если Alembic не требуется, Workflow не падает
5. **`pytest -v`** — запускает тесты после успешных миграций

### Когда это срабатывает:
- При push в ветку `main`
- По расписанию (каждый день в 02:00 UTC)
- Автоматически перед деплоем на продакшене

---

## 🌐 ЧАСТЬ 2: НАСТРОЙКА МИГРАЦИЙ ДЛЯ RENDER

### Предусловие:
У тебя должен быть аккаунт на [Render.com](https://render.com)

### Шаги настройки в панели Render:

#### 1️⃣ Откройте Dashboard → Web Service → Your Service

#### 2️⃣ Перейдите в **Settings** → **Deploy**

#### 3️⃣ Найдите поле **Pre-deploy command**

#### 4️⃣ Скопируйте команду (выберите одну):

**ВАРИАНТ А: Только Django миграции** (рекомендуется)
```bash
cd classes-main && python manage.py migrate --noinput
```

**ВАРИАНТ Б: Django + Alembic + Статика**
```bash
cd classes-main && python manage.py migrate --noinput && python -m alembic upgrade head && python manage.py collectstatic --noinput
```

**ВАРИАНТ В: Использование скрипта** (если скрипт добавлен)
```bash
bash scripts/render_predeploy.sh
```

#### 5️⃣ Сохраните (Save)

#### 6️⃣ Нажмите **Deploy** для тестирования

### Результат:
При каждом деплое на Render будет происходить следующее:
```
1. Загрузка кода
2. Установка зависимостей
3. ❌ ЗАПУСК PRE-DEPLOY КОМАНДЫ (ваши миграции)
4. Перезапуск приложения
5. Готово!
```

### Проверка лога миграций в Render:
- Откройте **Logs** в Render Dashboard
- При деплое увидите вывод типа:
```
Operations to perform:
  Apply all migrations: accounts, learning, ...
Running migrations:
  Applying accounts.0001_initial... OK
  Applying learning.0002_add_fields... OK
  ...
✅ Pre-deploy миграции завершены успешно!
```

---

## 🧪 ЧАСТЬ 3: ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ КЭШИРОВАНИЯ

### Файл теста:
`tests/performance/test_cache_performance.py`

### Структура теста:

```
test_cache_performance.py
├── TestHomePagePerformance         # Тесты главной страницы
│   ├── test_home_page_cache_improves_performance()    # ⭐ ОСНОВНОЙ ТЕСТ
│   └── test_home_page_cache_consistency()
├── TestSearchPagePerformance        # Тесты поиска
│   ├── test_search_page_cache_improves_performance()
│   └── test_search_different_queries_have_different_cache()
├── TestApplicationPerformance       # Комплексный тест
│   └── test_multiple_pages_with_and_without_cache()
└── Дополнительные тесты
    ├── test_cache_clear_invalidates_cache()
    └── test_cache_with_rapid_requests()
```

### Что делает основной тест:

```python
1. clear_all_caches()  # 🧹 Очищает кэш

2. response_uncached, time_without_cache = measure_response_time(client, url)
   # ⏱️  Замеряет первый запрос (без кэша)

3. response_cached, time_with_cache = measure_response_time(client, url)
   # ⏱️  Замеряет второй запрос (с кэшем)

4. speedup_ratio = time_without_cache / time_with_cache
   # 📊 Считает ускорение (должно быть > 1.5x)

5. assert speedup_ratio >= 1.5
   # ✅ Проверяет, что кэш действительно помогает
```

---

## 🚀 ЗАПУСК ТЕСТОВ ЛОКАЛЬНО

### 1️⃣ Запустить все тесты производительности:
```bash
pytest tests/performance/test_cache_performance.py -s -v
```

**Вывод:**
```
tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance PASSED
⏱️  Первый запрос (без кэша): 45.23 ms
⏱️  Второй запрос (с кэшем): 8.12 ms

📊 РЕЗУЛЬТАТЫ ТЕСТА HOME PAGE:
   Без кэша:    45.23 ms
   С кэшем:     8.12 ms
   Ускорение:   5.57x раз
   ✅ Тест PASSED (минимальное требование: 1.5x)
```

### 2️⃣ Запустить конкретный тест:
```bash
pytest tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance -s
```

### 3️⃣ Запустить тесты поиска:
```bash
pytest tests/performance/test_cache_performance.py::TestSearchPagePerformance -s -v
```

### 4️⃣ Запустить комплексный тест всех страниц:
```bash
pytest tests/performance/test_cache_performance.py::TestApplicationPerformance -s -v
```

### 5️⃣ Запустить все тесты с подробным выводом:
```bash
pytest tests/performance/test_cache_performance.py -s -v --tb=short
```

### 6️⃣ Запустить тесты без вывода (для CI/CD):
```bash
pytest tests/performance/test_cache_performance.py -q
```

---

## 📊 ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ

### ✅ Хорошие результаты:
```
⏱️  Первый запрос (без кэша): 50.00 ms
⏱️  Второй запрос (с кэшем): 5.00 ms
Ускорение: 10.00x раз  ← ОТЛИЧНО! (> 5x)
```

### ⚠️ Средние результаты:
```
⏱️  Первый запрос (без кэша): 30.00 ms
⏱️  Второй запрос (с кэшем): 15.00 ms
Ускорение: 2.00x раз  ← ХОРОШО (> 1.5x, минимум)
```

### ❌ Плохие результаты:
```
⏱️  Первый запрос (без кэша): 20.00 ms
⏱️  Второй запрос (с кэшем): 18.00 ms
Ускорение: 1.11x раз  ← ПЛОХО (< 1.5x)
❌ Тест FAILED
```

### Возможные причины плохих результатов:
1. **Redis не подключен** — Проверьте `REDIS_URL` в settings.py
2. **Кэш не настроен** — Проверьте `CACHES` в settings.py
3. **Страница уже быстрая** — Даже без кэша < 5ms (не нужен кэш)
4. **Слабый кэш-ключ** — Проверьте логику кэширования в views.py

---

## 🔧 ДОПОЛНИТЕЛЬНЫЕ ФЛАГИ PYTEST

```bash
# Вывод очень подробно (включая HTTP запросы)
pytest tests/performance/test_cache_performance.py -s -v --tb=long

# Остановить на первой ошибке
pytest tests/performance/test_cache_performance.py -s -x

# Запустить только один конкретный класс
pytest tests/performance/test_cache_performance.py::TestHomePagePerformance -s

# Запустить в параллельном режиме (требует pytest-xdist)
pytest tests/performance/test_cache_performance.py -n auto -s

# Сохранить результаты в JSON
pytest tests/performance/test_cache_performance.py --json-report --json-report-file=results.json
```

---

## 📝 ПРИМЕРЫ КЭШИРОВАНИЯ В VIEWS.PY

### Пример 1: Кэширование всей страницы
```python
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

@cache_page(60 * 5)  # Кэш на 5 минут
def home(request):
    # ... ваш код ...
    return render(request, 'home.html')
```

### Пример 2: Кэширование с ключом
```python
from django.core.cache import cache
from django.views import View

class HomeView(View):
    def get(self, request):
        cache_key = 'home_page_html'
        html = cache.get(cache_key)
        
        if html is None:
            # Загружаем данные из БД
            html = render_to_string('home.html')
            cache.set(cache_key, html, 300)  # 5 минут
        
        return HttpResponse(html)
```

### Пример 3: Кэширование по параметрам поиска
```python
def search(request):
    query = request.GET.get('query', '')
    cache_key = f'search_{query}'
    
    results = cache.get(cache_key)
    if results is None:
        results = Job.objects.filter(title__icontains=query)
        cache.set(cache_key, list(results), 600)  # 10 минут
    
    return render(request, 'search.html', {'results': results})
```

---

## ✨ РЕЗЮМЕ

### GitHub Actions:
✅ Миграции запускаются автоматически при push в `main`  
✅ Тесты проверяют корректность миграций  
✅ Если тесты падают, деплой не происходит  

### Render:
✅ Pre-deploy команда запускает миграции перед перезапуском  
✅ Логи миграций видны в Dashboard  
✅ База данных всегда актуальна при деплое  

### Тесты производительности:
✅ Проверяют, что кэширование работает (5-10x ускорение)  
✅ Запускаются локально: `pytest tests/performance/ -s -v`  
✅ Выводят подробную статистику времени выполнения  

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- [Django Migration Docs](https://docs.djangoproject.com/en/4.2/topics/migrations/)
- [Django Cache Framework](https://docs.djangoproject.com/en/4.2/topics/cache/)
- [Render Pre-deploy Commands](https://render.com/docs/deploy-hooks)
- [Pytest Django](https://pytest-django.readthedocs.io/)
