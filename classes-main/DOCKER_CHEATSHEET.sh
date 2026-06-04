#!/usr/bin/env bash

# 🐳 DOCKER COMPOSE CHEATSHEET
# Быстрые команды для работы с Docker

# ============================================================================
# 🚀 ЗАПУСК
# ============================================================================

# Запустить ВСЕ контейнеры в фоне
docker-compose up -d

# Запустить ВСЕ контейнеры с выводом логов (Ctrl+C чтобы выйти)
docker-compose up

# Запустить конкретный сервис
docker-compose up -d web
docker-compose up -d redis
docker-compose up -d db

# ============================================================================
# ⏹️  ОСТАНОВКА
# ============================================================================

# Остановить ВСЕ контейнеры
docker-compose down

# Остановить все и удалить volumes (БД будет очищена!)
docker-compose down -v

# Остановить конкретный сервис
docker-compose stop web
docker-compose stop db
docker-compose stop redis

# ============================================================================
# 📊 СТАТУС И ЛОГИ
# ============================================================================

# Посмотреть статус всех контейнеров
docker-compose ps

# Посмотреть логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web      # Django приложение
docker-compose logs -f celery   # Celery worker
docker-compose logs -f db       # PostgreSQL
docker-compose logs -f redis    # Redis

# Последние 50 строк
docker-compose logs --tail=50 web

# ============================================================================
# 🔄 ПЕРЕЗАПУСК
# ============================================================================

# Перезапустить все
docker-compose restart

# Перезапустить конкретный сервис
docker-compose restart web
docker-compose restart db

# Перестроить образы и запустить
docker-compose up -d --build

# ============================================================================
# 💻 ВЫПОЛНЕНИЕ КОМАНД В КОНТЕЙНЕРЕ
# ============================================================================

# Django команды
docker-compose exec web python manage.py migrate              # Миграции
docker-compose exec web python manage.py createsuperuser    # Создать админа
docker-compose exec web python manage.py seed_learning      # Заполнить БД
docker-compose exec web python manage.py shell              # Django shell
docker-compose exec web python manage_cache.py clear        # Очистить кэш
docker-compose exec web python manage_cache.py stats        # Статистика кэша
docker-compose exec web python manage_cache.py test-redis   # Тест Redis

# 🧪 ЗАПУСК ТЕСТОВ
docker-compose exec web pytest tests/performance/ -s -v     # Performance тесты
docker-compose exec web pytest tests/unit/ -v               # Unit тесты
docker-compose exec web pytest --cov=. --cov-report=html    # С покрытием

# Bash в контейнере
docker-compose exec web bash

# ============================================================================
# 🐘 POSTGRESQL КОМАНДЫ
# ============================================================================

# Вход в psql
docker-compose exec db psql -U postgres -d simulator_db

# Дамп БД
docker-compose exec db pg_dump -U postgres simulator_db > backup.sql

# Восстановить БД
docker-compose exec -T db psql -U postgres simulator_db < backup.sql

# ============================================================================
# 🔴 REDIS КОМАНДЫ
# ============================================================================

# Вход в redis-cli
docker-compose exec redis redis-cli

# Посмотреть все ключи
docker-compose exec redis redis-cli KEYS "*"

# Очистить Redis
docker-compose exec redis redis-cli FLUSHALL

# ============================================================================
# 🧹 ОЧИСТКА
# ============================================================================

# Удалить контейнеры (но не volumes)
docker-compose rm -f

# Удалить всё (контейнеры, networks, volumes - БУДУТ ПОТЕРЯНЫ ДАННЫЕ!)
docker-compose down -v

# Очистить все Docker ресурсы (осторожно!)
docker system prune -a --volumes

# ============================================================================
# 📈 ИНФОРМАЦИЯ
# ============================================================================

# Версия Docker
docker --version
docker-compose --version

# Информация о контейнерах
docker ps -a
docker images

# Статистика использования ресурсов
docker stats

# Информация о volumes
docker volume ls
docker volume inspect classes-main_postgres_data

# ============================================================================
# 🔧 ОТЛАДКА
# ============================================================================

# Проверить конфигурацию docker-compose.yml
docker-compose config

# Валидировать docker-compose.yml
docker-compose config --quiet

# Посмотреть переменные окружения в контейнере
docker-compose exec web env

# Посмотреть текущую рабочую директорию
docker-compose exec web pwd

# ============================================================================
# 🚀 БЫСТРЫЕ КОМБО
# ============================================================================

# Полный рестарт (чистая база)
docker-compose down -v && docker-compose up -d && docker-compose exec web python manage.py migrate

# Запустить с миграциями и сидом
docker-compose up -d && docker-compose exec web python manage.py migrate && docker-compose exec web python manage.py seed_learning

# Запустить все тесты
docker-compose up -d && docker-compose exec web pytest --cov=. --cov-report=html -v

# Просмотреть логи web и остановить
docker-compose logs -f web | head -n 100 && docker-compose stop

# ============================================================================
# 📝 ПРИМЕРЫ РАБОТЫ
# ============================================================================

# Пример: Запустить контейнеры и проверить статус
# $ docker-compose up -d
# $ docker-compose ps
# NAME                  STATUS
# simulator-web         Up (healthy)
# simulator-redis       Up
# simulator-db          Up (healthy)
# simulator-celery      Up
# simulator-celery-beat Up

# Пример: Запустить тесты производительности
# $ docker-compose exec web pytest tests/performance/test_cache_performance.py -s -v
# ⏱️  Первый запрос (без кэша): 45.23 ms
# ⏱️  Второй запрос (с кэшем): 8.91 ms
# Ускорение: 5.31x раз
# ✅ 7 passed

# Пример: Проверить логи
# $ docker-compose logs -f web
# [2026-06-02] Starting development server at http://localhost:8000/
# [2026-06-02] Django version 4.2.x
# [2026-06-02] Server is running. Quit with CONTROL-C.

# ============================================================================
# 💡 СОВЕТЫ
# ============================================================================

# Используй -d флаг для фонового запуска
# docker-compose up -d

# Используй --rm для удаления контейнера после выполнения
# docker-compose run --rm test

# Используй -T флаг при pipe операциях
# docker-compose exec -T db psql ... < backup.sql

# Смотри логи в отдельном окне терминала
# docker-compose logs -f web

# ============================================================================
# ❌ ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ
# ============================================================================

# Ошибка: "port is already in use"
# Решение: docker-compose down && docker-compose up -d

# Ошибка: "database is locked"
# Решение: docker-compose restart db

# Ошибка: "connection refused"
# Решение: Убедись что зависимые контейнеры запущены
# docker-compose exec web python manage_cache.py test-redis

# Ошибка: "No such container"
# Решение: Запусти контейнеры
# docker-compose up -d

# ============================================================================

echo "✅ Все команды в одном месте!"
echo "📖 Для подробной информации смотри: DOCKER_GUIDE.md"
