#!/bin/bash
set -euo pipefail

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="${BACKUP_DIR:-backups}"
DB_URL="${DATABASE_URL:-${PGDATABASE_URL:-postgresql://postgres:postgres@db:5432/app}}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

mkdir -p "$BACKUP_DIR"

echo "[backup] Using database URL: ${DB_URL%%@*}@***"
echo "[backup] Saving to $BACKUP_DIR/backup_$DATE.sql"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump not found. Install PostgreSQL client tools."
  exit 1
fi

pg_dump "$DB_URL" > "$BACKUP_DIR/backup_$DATE.sql"

if [ -f "$BACKUP_DIR/backup_$DATE.sql" ]; then
  echo "✅ Backup created: $BACKUP_DIR/backup_$DATE.sql"
fi
find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete
echo "🗑️ Old backups deleted (older than $RETENTION_DAYS days)"
