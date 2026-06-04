# 🐳 DOCKER ИНСТРУКЦИЯ: Локальная разработка и deployment

**Последнее обновление:** 2 июня 2026 г.

---

## 📋 СОДЕРЖАНИЕ

1. [Быстрый старт](#быстрый-старт)
2. [Команды Docker Compose](#команды-docker-compose)
3. [Запуск тестов в Docker](#запуск-тестов-в-docker)
4. [Отладка](#отладка)
5. [Production Deployment](#production-deployment)

---

## 🚀 БЫСТРЫЙ СТАРТ (5 минут)

### Предусловия
- Установлен Docker Desktop (https://www.docker.com/products/docker-desktop)
- Git репозиторий клонирован

### 1️⃣ Запустить все контейнеры
```bash
cd classes-main
docker-compose up -d
```

**Что запустится:**
- ✅ `web` — Django приложение на http://localhost:8000
- ✅ `redis` — Кэш на http://localhost:6379
- ✅ `db` — PostgreSQL на http://localhost:5432
- ✅ `celery` — Worker для асинхронных задач
- ✅ `celery-beat` — Scheduler для расписания

### 2️⃣ Проверить что всё работает
```bash
# Посмотреть статус контейнеров
docker-compose ps

# Должно быть:
# NAME                  STATUS
# simulator-web         Up (healthy)
# simulator-redis       Up
# simulator-db          Up (healthy)
# simulator-celery      Up
# simulator-celery-beat Up
```

### 3️⃣ Открыть приложение
```
http://localhost:8000
```

### 4️⃣ Остановить контейнеры
```bash
docker-compose down
```

---

## 🐳 КОМАНДЫ DOCKER COMPOSE

### Запуск и остановка

```bash
# Запустить все контейнеры в фоне
docker-compose up -d

# Запустить все контейнеры с выводом логов
docker-compose up

# Остановить все контейнеры
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v

# Перезапустить контейнеры
docker-compose restart

# Перестроить образ (после изменения requirements.txt)
docker-compose up -d --build
```

### Просмотр логов

```bash
# Логи всех контейнеров
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f redis
docker-compose logs -f db

# Последние N строк логов
docker-compose logs --tail=100 web

# Логи с временем
docker-compose logs -f -t web
```

### Управление сервисами

```bash
# Остановить конкретный сервис
docker-compose stop web
docker-compose stop db

# Запустить остановленный сервис
docker-compose start web

# Перезапустить сервис
docker-compose restart web

# Удалить контейнер (но не volume)
docker-compose rm -f web
```

### Выполнение команд в контейнере

```bash
# Запустить Django команду
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_learning

# Запустить Django shell
docker-compose exec web python manage.py shell

# Запустить bash в контейнере
docker-compose exec web bash

# Запустить команду в Redis
docker-compose exec redis redis-cli
```

---

## 🧪 ЗАПУСК ТЕСТОВ В DOCKER

### Вариант 1: Запустить тесты отдельным контейнером
```bash
# Запустить тесты производительности
docker-compose run --rm test

# Это запустит:
# pytest tests/performance/test_cache_performance.py -s -v --cov=. --cov-report=html
```

### Вариант 2: Запустить тесты в контейнере web
```bash
# Все тесты с покрытием
docker-compose exec web pytest --cov=. --cov-report=html --cov-report=term-missing -v

# Только performance тесты
docker-compose exec web pytest tests/performance/test_cache_performance.py -s -v

# Только unit тесты
docker-compose exec web pytest tests/unit/ -v

# Конкретный тест
docker-compose exec web pytest tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance -s
```

### Вариант 3: Запустить тесты локально (без Docker)
```bash
cd classes-main
pytest tests/performance/ -s -v
```

### Пример вывода
```
=============== test session starts ===============
tests/performance/test_cache_performance.py::TestHomePagePerformance::test_home_page_cache_improves_performance PASSED
⏱️  Первый запрос (без кэша): 45.23 ms
⏱️  Второй запрос (с кэшем): 8.91 ms
Ускорение: 5.31x раз

7 passed in 2.45s
=============== Coverage report ===============
```

---

## 🔧 ОТЛАДКА

### Проблема: Контейнер не запускается
```bash
# Посмотреть логи
docker-compose logs web

# Перестроить образ
docker-compose down -v
docker-compose up -d --build
```

### Проблема: БД недоступна
```bash
# Проверить статус БД
docker-compose logs db

# Перезапустить БД
docker-compose restart db

# Удалить все данные БД и пересоздать
docker-compose down -v
docker-compose up -d
```

### Проблема: Redis не подключен
```bash
# Проверить статус Redis
docker-compose logs redis

# Тест подключения Redis
docker-compose exec web python manage_cache.py test-redis

# Перезапустить Redis
docker-compose restart redis
```

### Проблема: Port уже занят
```bash
# Найти что использует порт 8000
lsof -i :8000

# Использовать другой порт в docker-compose.yml
# ports:
#   - "9000:8000"  ← Изменить на 9000
```

### Проблема: Миграции не применяются
```bash
# Запустить миграции вручную
docker-compose exec web python manage.py migrate

# Смотреть статус миграций
docker-compose exec web python manage.py showmigrations

# Откатить миграцию
docker-compose exec web python manage.py migrate accounts 0001
```

---

## 📊 DOCKER COMPOSE СТРУКТУРА

```
services:
├── web                 # Django приложение (Gunicorn)
│   ├── Port: 8000
│   ├── Health check: http://localhost:8000/health
│   └── Автоматически запускает миграции
│
├── redis              # Кэш и очередь задач
│   ├── Port: 6379
│   └── Volume: redis_data:/data
│
├── db                 # PostgreSQL БД
│   ├── Port: 5432
│   ├── User: postgres
│   ├── Password: postgres
│   ├── Database: simulator_db
│   └── Volume: postgres_data:/var/lib/postgresql/data
│
├── celery             # Worker для асинхронных задач
│   └── 4 processes
│
├── celery-beat        # Scheduler для расписания
│   └── DatabaseScheduler
│
└── test               # Контейнер для запуска тестов
    └── Запускается по требованию
```

---

## 🌍 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

### Для разработки (docker-compose.yml)
```yaml
DATABASE_URL=postgresql://postgres:postgres@db:5432/simulator_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
DEBUG=True
```

### Для production (используй .env файл)
```bash
# .env (не добавлять в git!)
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://user:password@host:6379/0
```

---

## 💾 VOLUMES И DATA

### Какие volumes есть
```yaml
postgres_data:    # БД PostgreSQL
redis_data:       # Данные Redis
logs:             # Логи приложения
```

### Как посмотреть volumes
```bash
docker volume ls
docker volume inspect classes-main_postgres_data
```

### Как очистить volumes
```bash
# Удалить все volumes (потеряются все данные!)
docker-compose down -v

# Удалить конкретный volume
docker volume rm classes-main_postgres_data
```

### Как делать бэкап БД
```bash
# Дамп БД
docker-compose exec db pg_dump -U postgres simulator_db > backup.sql

# Восстановить БД из дампа
docker-compose exec -T db psql -U postgres simulator_db < backup.sql
```

---

## 🐳 DOCKERFILE ДЕТАЛИ

```dockerfile
# FROM python:3.13-slim
# Используем легкий образ Python 3.13

# WORKDIR /app
# Рабочая директория внутри контейнера

# RUN pip install -r requirements.txt
# Установка зависимостей

# HEALTHCHECK
# Проверка что приложение живо каждые 30 сек

# CMD gunicorn core.wsgi:application
# Запуск приложения с 4 workers
```

---

## 📈 PERFORMANCE И ОПТИМИЗАЦИЯ

### Количество workers Gunicorn
```bash
# Текущие настройки: 4 workers
# Для оптимизации: (CPU cores * 2) + 1
# Пример: 2 ядра CPU = (2*2)+1 = 5 workers

# Изменить в docker-compose.yml:
# gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 5
```

### Количество processes Celery
```bash
# Текущие настройки: 4 processes
# Можно увеличить если много задач

# Изменить в docker-compose.yml:
# celery -A core worker --loglevel=info --concurrency=8
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Для Render.com
```yaml
# render.yaml

services:
  - type: docker
    name: simulator-backend
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        value: ${{DATABASE_URL}}
      - key: REDIS_URL
        value: ${{REDIS_URL}}
```

### Pre-deploy command для Render
```bash
# Того что в docker-compose.yml хватит, так как:
# CMD уже включает миграции и seed
```

### Docker Hub (для deployment)
```bash
# Собрать образ
docker build -t yourusername/simulator-backend .

# Залить на Docker Hub
docker push yourusername/simulator-backend

# Использовать в production
docker pull yourusername/simulator-backend
docker run -d -p 8000:8000 yourusername/simulator-backend
```

---

## 📚 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Информация о Docker образах
docker images

# Информация о контейнерах
docker ps -a

# Очистить всё (осторожно!)
docker system prune -a --volumes

# Статистика использования ресурсов
docker stats

# Вход в контейнер
docker exec -it simulator-web bash

# Посмотреть переменные окружения контейнера
docker exec simulator-web env
```

---

## 🎯 ЧЕКЛИСТ ДЛЯ РАЗРАБОТКИ

- [ ] Установлен Docker Desktop
- [ ] Репозиторий клонирован
- [ ] `cd classes-main`
- [ ] `docker-compose up -d`
- [ ] `docker-compose ps` показывает все контейнеры healthy
- [ ] http://localhost:8000 открывается
- [ ] `docker-compose exec web pytest tests/performance/ -s -v` проходит
- [ ] `docker-compose logs web` показывает что приложение работает

---

## 🆘 БЫСТРАЯ ПОМОЩЬ

| Проблема | Команда |
|----------|---------|
| Контейнер не запускается | `docker-compose logs web` |
| Миграции не применяются | `docker-compose exec web python manage.py migrate` |
| Тесты падают | `docker-compose exec web pytest -s` |
| БД недоступна | `docker-compose restart db` |
| Redis не работает | `docker-compose restart redis` |
| Память переполнена | `docker system prune -a --volumes` |

---

## 📖 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Хорошего развития!** 🚀
