#!/usr/bin/env bash
set -e

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$WORKDIR"

DATE="$(date +%Y_%m_%d)"
BACKUP_FILE="backup_${DATE}.sql"
BACKUP_DIR="/app/backups"

echo "Создание бэкапа..."

docker compose exec -T web sh -c "mkdir -p ${BACKUP_DIR} && pg_dump -U postgres -h db -d simulator_db > ${BACKUP_DIR}/${BACKUP_FILE}"

echo "Файл ${BACKUP_FILE} успешно создан"

echo "Сбор статических файлов..."

docker compose exec -T web python manage.py collectstatic --noinput

echo "Collecting static files... OK"

echo "Применение миграций..."

docker compose exec -T web python manage.py migrate --noinput

echo "Applying migrations... OK"
