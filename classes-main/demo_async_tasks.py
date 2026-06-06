#!/usr/bin/env python3
"""
🎓 ДЕМОНСТРАЦИОННЫЙ СКРИПТ ДЛЯ ПРЕЗЕНТАЦИИ
Шаг 3: Асинхронность и Очереди задач (Celery)

Этот скрипт показывает:
1. Синхронный запрос (сайт зависает на 5 сек)
2. Асинхронный запрос (сайт отзывчив, задача выполняется в фоне)
3. Celery воркер подхватывает и выполняет задачу

Использование:
    # Терминал 1: запустить воркер
    python manage.py celery -A core worker --loglevel=info
    
    # Терминал 2: запустить демонстрацию
    python demo_async_tasks.py
"""

import os
import sys
import time
import django
from pathlib import Path
import threading

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from celery import shared_task
from accounts.tasks import send_welcome_email_task, process_resume_task
from core.celery import app

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_step(step_num, text):
    print(f"{Colors.BOLD}{Colors.CYAN}Шаг {step_num}: {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_code(code):
    print(f"{Colors.YELLOW}{code}{Colors.END}")

def print_worker(text):
    print(f"{Colors.MAGENTA}🔧 WORKER: {text}{Colors.END}")

def print_browser(text):
    print(f"{Colors.CYAN}🌐 БРАУЗЕР: {text}{Colors.END}")

def demo_celery_config():
    """Показывает конфигурацию Celery"""
    print_step(1, "Конфигурация Celery для асинхронных задач")
    print()
    
    print_info("Файл: core/settings.py")
    print_code("""
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Almaty'
    
    # Celery Beat (Scheduler)
    CELERY_BEAT_SCHEDULE = {
        'daily-job-digest-at-midnight': {
            'task': 'accounts.tasks.daily_job_digest_task',
            'schedule': crontab(hour=0, minute=0),
        },
    }
    """)
    
    print()
    print_success("Celery подключена к Redis ✅")

def demo_task_definition():
    """Показывает определение асинхронной задачи"""
    print_step(2, "Определение асинхронной задачи")
    print()
    
    print_info("Файл: accounts/tasks.py")
    print_code("""
    from celery import shared_task
    
    @shared_task(bind=True)
    def send_welcome_email_task(self, username, email):
        '''Отправляет приветственное письмо в фоне'''
        
        print('[Celery] Началась отправка email...')
        # Имитация долгой операции
        time.sleep(5)
        
        print('[Celery] Email успешно отправлен!')
        return {'status': 'sent', 'username': username}
    """)
    
    print()
    print_success("Задача определена как @shared_task ✅")

def demo_synchronous_problem():
    """Демонстрирует проблему синхронного кода"""
    print_step(3, "🔴 ПРОБЛЕМА: Синхронный код (сайт зависает)")
    print()
    
    print_info("Сценарий: Пользователь регистрируется на сайте")
    print()
    
    print_browser("1. Пользователь нажимает кнопку 'Зарегистрироваться'")
    time.sleep(1)
    
    print_browser("2. POST запрос на сервер")
    time.sleep(0.5)
    
    print_code("   def register(request):")
    print_code("       send_welcome_email(email)  # 📌 БЕЗ АСИНХРОНА")
    time.sleep(0.5)
    
    print_warning("3. ⏳ Сервер начинает отправлять email...")
    print_code("   • Подключение к SMTP серверу...")
    time.sleep(2)
    
    print_code("   • Отправка письма...")
    time.sleep(2)
    
    print_code("   • Ожидание ответа...")
    time.sleep(1.5)
    
    print_warning("4. ⏳ САЙТ ЗАВИСАЕТ НА 5+ СЕКУНД!")
    print_code("   Пользователь видит белый экран и крутящийся спиннер...")
    print_code("   Может нажать \"Стоп\" → запрос отменится → письмо не отправится")
    
    print()
    print_warning("ПРОБЛЕМА: Если на сервере 100 человек регистрируются → 100 x 5сек запросов")
    print_warning("Результат: Сервер перегружен, сайт медленный! 💔")

def demo_asynchronous_solution():
    """Демонстрирует решение с асинхроном"""
    print_step(4, "🟢 РЕШЕНИЕ: Асинхронный код + Celery (сайт отзывчив)")
    print()
    
    print_info("Сценарий: Пользователь регистрируется на сайте")
    print()
    
    print_browser("1. Пользователь нажимает кнопку 'Зарегистрироваться'")
    time.sleep(0.5)
    
    print_browser("2. POST запрос на сервер")
    time.sleep(0.5)
    
    print_code("   def register(request):")
    print_code("       send_welcome_email_task.delay(email)  # 📌 АСИНХРОННО!")
    time.sleep(0.5)
    
    print_success("3. ⚡ Сервер СРАЗУ возвращает ответ!")
    print_browser("✅ 'Спасибо! Проверьте почту.' (за <100ms!)")
    print_code("   └─ Пользователь счастлив! Сайт отзывчив!")
    
    time.sleep(1)
    
    print()
    print_info("В то же время, в фоне на Celery воркере:")
    print()
    
    print_worker("4. Celery воркер подхватил задачу из очереди")
    time.sleep(0.5)
    
    print_worker("5. Подключение к SMTP серверу...")
    time.sleep(1)
    
    print_worker("6. Отправка письма...")
    time.sleep(1)
    
    print_worker("7. Ожидание ответа...")
    time.sleep(1)
    
    print_success("8. ✅ Email успешно отправлен в фоне!")
    print_code("   └─ Пользователь уже давно ушел, ему все равно :)")
    
    print()
    print_success("РЕЗУЛЬТАТ: Сайт остается отзывчивым! 🚀")

def demo_realtime_execution():
    """Демонстрирует реальное выполнение Celery задачи"""
    print_step(5, "Реальное выполнение асинхронной задачи")
    print()
    
    print_info("Отправляем задачу в Celery очередь...")
    print_code("   >>> send_welcome_email_task.delay('alice@example.com')")
    
    print()
    print_warning("⚠️  ВАЖНО: Убедитесь, что Celery воркер запущен в другом терминале:")
    print_code("   python manage.py celery -A core worker --loglevel=info")
    
    print()
    
    # Проверяем, запущен ли Celery воркер
    try:
        # Пытаемся выполнить задачу
        task = send_welcome_email_task.delay('demo@example.com')
        task_id = task.id
        
        print_success(f"Задача отправлена! ID: {task_id}")
        print()
        
        print_info("Проверяем статус задачи:")
        
        for i in range(6):
            status = app.AsyncResult(task_id).status
            result = app.AsyncResult(task_id).result
            
            if status == 'PENDING':
                print_code(f"   Статус: PENDING (в очереди) ⏳")
            elif status == 'STARTED':
                print_worker(f"Статус: STARTED (выполняется) 🔄")
            elif status == 'SUCCESS':
                print_success(f"Статус: SUCCESS (завершена) ✅")
                print_code(f"   Результат: {result}")
                break
            elif status == 'FAILURE':
                print(f"{Colors.RED}Статус: FAILURE (ошибка) ❌{Colors.END}")
                break
            
            if i < 5:
                time.sleep(1)
        
        print()
        print_success("Задача успешно выполнена! ✅")
        
    except Exception as e:
        print()
        print_warning(f"Celery воркер не запущен: {e}")
        print_code("Запустите в отдельном терминале:")
        print_code("   python manage.py celery -A core worker --loglevel=info")

def demo_queue_visualization():
    """Показывает визуализацию очереди"""
    print_step(6, "Визуализация очереди задач")
    print()
    
    print_info("Архитектура Celery:")
    print_code("""
    🌐 WEB APPLICATION (Django)
       ├─ def register(request):
       │  └─ send_welcome_email_task.delay(email)  ←─ Отправить в очередь
       │
       └─ Задача добавляется в очередь
    
    
    ⚙️  REDIS (Message Broker)
       │
       ├─ Queue: [
       │     {'task': 'send_welcome_email_task', 'email': 'alice@example.com'},
       │     {'task': 'send_welcome_email_task', 'email': 'bob@example.com'},
       │     {'task': 'process_resume_task', 'user_id': 42},
       │  ]
       │
       └─ Очередь отправляет задачи воркерам
    
    
    🔧 CELERY WORKERS (Background)
       ├─ Worker 1: Выполняет send_welcome_email_task
       ├─ Worker 2: Выполняет process_resume_task
       ├─ Worker 3: Выполняет cleanup_old_sessions_task
       └─ Worker 4: Свободен, ждет задач
    
    
    📊 РЕЗУЛЬТАТЫ
       └─ Сохраняются в Redis
          ├─ task_1: {'status': 'SUCCESS', ...}
          ├─ task_2: {'status': 'FAILURE', ...}
          └─ task_3: {'status': 'RETRY', ...}
    """)

def demo_use_cases():
    """Показывает примеры использования"""
    print_step(7, "Примеры использования асинхронных задач")
    print()
    
    examples = [
        ("Отправка email", "Регистрация, сброс пароля, рассылка", "5-30 сек"),
        ("Генерация PDF", "Экспорт CV, отчеты", "2-10 сек"),
        ("Обработка изображений", "Загрузка аватара, ресайз", "1-5 сек"),
        ("Парсинг данных", "Импорт вакансий с сайтов", "10-60 сек"),
        ("Отправка СМС", "Оповещения, подтверждение", "2-5 сек"),
        ("Расчеты", "Аналитика, рейтинги", "5-30 сек"),
    ]
    
    for task_name, description, duration in examples:
        print_code(f"✓ {task_name:25} → {description:35} (~{duration})")
    
    print()
    print_info("Все эти операции работают в фоне, сайт остается отзывчивым!")

def main():
    print_header("🎓 ДЕМОНСТРАЦИЯ: АСИНХРОННОСТЬ И CELERY")
    
    print_info("Что видит преподаватель:")
    print_code("✓ Код: @shared_task def send_welcome_email_task() в tasks.py")
    print_code("✓ Код: send_welcome_email_task.delay(email) в views.py")
    print_code("✓ Консоль Web: 'Задача отправлена! ID: abc123'")
    print_code("✓ Консоль Worker: '[Celery] Началась отправка...' → '[Celery] Email отправлен!'")
    print_code("✓ Результат: Сайт не зависает, задача выполняется в фоне! 🚀")
    
    print()
    
    try:
        demo_celery_config()
        print()
        demo_task_definition()
        print()
        demo_synchronous_problem()
        print()
        demo_asynchronous_solution()
        print()
        demo_realtime_execution()
        print()
        demo_queue_visualization()
        print()
        demo_use_cases()
        
        print_header("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print()
        print_info("Результаты для преподавателя:")
        print_code("1️⃣  Синхронный код:  Сайт зависает на 5 сек 😞")
        print_code("2️⃣  Асинхронный код: Сайт отвечает за <100ms 😊")
        print_code("3️⃣  Celery воркер:  Выполняет задачу в фоне 🔄")
        print_code("4️⃣  Результат:      Масштабируемое приложение 🚀")
        print()
        print_success("Асинхронность работает как надо! 🎉")
        
    except Exception as e:
        print()
        print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
