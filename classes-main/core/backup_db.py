import shutil
import os
from datetime import datetime

def make_backup():
    source = 'db.sqlite3'
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    destination = f'{backup_dir}/db_backup_{timestamp}.sqlite3'
    
    if os.path.exists(source):
        shutil.copy2(source, destination)
        print(f"✅ Резервная копия создана: {destination}")
    else:
        print("❌ Файл базы данных не найден.")

if __name__ == "__main__":
    make_backup()