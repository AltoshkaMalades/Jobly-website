# Build dependencies in an isolated stage, then copy only installed packages into runtime.
FROM python:3.13-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS runtime

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем буферизацию логов Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

# Копируем весь код проекта
COPY . /app/

# Создаем папку для логов
RUN mkdir -p /app/logs

# Открываем порт 8000
EXPOSE 8000

# Health check (проверяет что приложение живо)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Команда по умолчанию (собирает статику, запускает миграции, очищает OAuth дубликаты, настраивает OAuth и сервер)
CMD ["sh", "-c", "set -e; \
    echo '=== Collecting static files ===' && python manage.py collectstatic --noinput && \
    echo '=== Running migrations ===' && python manage.py migrate --noinput && \
    echo '=== Cleaning up duplicate OAuth apps ===' && python manage.py cleanup_socialapps && \
    echo '=== Setting up Google OAuth ===' && python manage.py setup_google_oauth && \
    echo '=== Seeding learning content ===' && python manage.py seed_learning && \
    echo '=== Starting Gunicorn server ===' && \
    gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 60 --access-logfile - --error-logfile -"]