#!/bin/bash

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="backups"
DB_URL="postgresql://jobly_10g5_user:InGiyZZmMa2qFe5N3cPzcnzXU0Ywkk3H@dpg-d86ss6gjo6nc73es230g-a.frankfurt-postgres.render.com/jobly_10g5"

mkdir -p $BACKUP_DIR

pg_dump $DB_URL > $BACKUP_DIR/backup_$DATE.sql

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_DIR/backup_$DATE.sql"
else
    echo "❌ Error!"
fi

find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
echo "🗑️Old backups deleted"