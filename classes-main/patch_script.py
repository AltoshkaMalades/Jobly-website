from pathlib import Path
from celery.schedules import crontab

settings = Path('core/settings.py')
text = settings.read_text(encoding='utf-8')
old = """CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
# --- ВАЖНОЕ ДОПОЛНЕНИЕ ---
# Указываем Django, куда перенаправлять неавторизованных пользователей
LOGIN_URL = 'login'
"""
new = """CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'daily-job-digest-at-midnight': {
        'task': 'accounts.tasks.daily_job_digest_task',
        'schedule': crontab(hour=0, minute=0),
        'args': (),
    },
    'cleanup-old-sessions-every-15-minutes': {
        'task': 'accounts.tasks.cleanup_old_sessions_task',
        'schedule': 15 * 60,
        'args': (),
    },
}
# --- ВАЖНОЕ ДОПОЛНЕНИЕ ---
# Указываем Django, куда перенаправлять неавторизованных пользователей
LOGIN_URL = 'login'
"""
if old not in text:
    raise SystemExit('Settings chunk not found')
settings.write_text(text.replace(old, new), encoding='utf-8')

backup = Path('backup.sh')
backup.write_text("""#!/bin/bash
set -euo pipefail

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR=\"${BACKUP_DIR:-backups}\"
DB_URL=\"${DATABASE_URL:-${PGDATABASE_URL:-postgresql://postgres:postgres@db:5432/app}}\"
RETENTION_DAYS=\"${RETENTION_DAYS:-7}\"

mkdir -p \"$BACKUP_DIR\"

echo \"[backup] Using database URL: ${DB_URL%%@*}@***\"
echo \"[backup] Saving to $BACKUP_DIR/backup_$DATE.sql\"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo \"pg_dump not found. Install PostgreSQL client tools.\"
  exit 1
fi

pg_dump \"$DB_URL\" > \"$BACKUP_DIR/backup_$DATE.sql\"

echo \"✅ Backup created: $BACKUP_DIR/backup_$DATE.sql\"
find \"$BACKUP_DIR\" -name \"*.sql\" -mtime +$RETENTION_DAYS -delete
echo \"🗑️ Old backups deleted (older than $RETENTION_DAYS days)\"
""", encoding='utf-8')
