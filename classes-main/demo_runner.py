#!/usr/bin/env python3
"""
🎓 ГЛАВНЫЙ ДЕМОНСТРАЦИОННЫЙ СКРИПТ
Запускает все 3 демонстрации по очереди

Использование:
    python demo_runner.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    banner = f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          🎓 ДЕМОНСТРАЦИОННЫЙ RUNNER ДЛЯ ПРЕЗЕНТАЦИИ             ║
║                                                                  ║
║     Шаг 1: CI/CD Pipeline (Бэкап + Миграции)                    ║
║     Шаг 2: Кэширование (Производительность)                     ║
║     Шаг 3: Асинхронность (Celery + Очереди)                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def print_menu():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}Выберите демонстрацию:{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    print(f"{Colors.BOLD}1.{Colors.END} {Colors.CYAN}🚀 Шаг 1: CI/CD Pipeline{Colors.END} (Бэкап + Миграции)")
    print(f"{Colors.BOLD}2.{Colors.END} {Colors.CYAN}⚡ Шаг 2: Кэширование{Colors.END} (Производительность)")
    print(f"{Colors.BOLD}3.{Colors.END} {Colors.CYAN}🔄 Шаг 3: Асинхронность{Colors.END} (Celery)")
    print(f"{Colors.BOLD}4.{Colors.END} {Colors.GREEN}🎬 Запустить все 3 демонстрации подряд{Colors.END}")
    print(f"{Colors.BOLD}5.{Colors.END} {Colors.YELLOW}📖 Показать руководство (DEMO_GUIDE.md){Colors.END}")
    print(f"{Colors.BOLD}0.{Colors.END} {Colors.RED}Выход{Colors.END}\n")

def run_demo(demo_number):
    """Запускает демонстрацию"""
    
    scripts = {
        1: ('demo_cicd_pipeline.py', '🚀 Шаг 1: CI/CD Pipeline'),
        2: ('demo_caching_performance.py', '⚡ Шаг 2: Кэширование'),
        3: ('demo_async_tasks.py', '🔄 Шаг 3: Асинхронность'),
    }
    
    if demo_number not in scripts:
        print(f"{Colors.RED}❌ Неверный номер демонстрации{Colors.END}")
        return
    
    script, title = scripts[demo_number]
    script_path = Path(script)
    
    if not script_path.exists():
        print(f"{Colors.RED}❌ Файл не найден: {script}{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}▶️  Запуск: {title}{Colors.END}\n")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=False)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏸️  Демонстрация остановлена пользователем{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка при запуске: {e}{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.GREEN}✅ Демонстрация завершена!{Colors.END}\n")

def run_all_demos():
    """Запускает все 3 демонстрации подряд"""
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}▶️  Запуск всех 3 демонстраций подряд...{Colors.END}\n")
    
    scripts = [
        ('demo_cicd_pipeline.py', '🚀 Шаг 1: CI/CD Pipeline'),
        ('demo_caching_performance.py', '⚡ Шаг 2: Кэширование'),
        ('demo_async_tasks.py', '🔄 Шаг 3: Асинхронность'),
    ]
    
    for i, (script, title) in enumerate(scripts, 1):
        script_path = Path(script)
        
        if not script_path.exists():
            print(f"{Colors.RED}❌ Файл не найден: {script}{Colors.END}\n")
            continue
        
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}[{i}/3] {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        try:
            subprocess.run([sys.executable, str(script_path)], check=False)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏸️  Демонстрация остановлена пользователем{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Ошибка при запуске: {e}{Colors.END}")
        
        if i < 3:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⏳ Пауза перед следующей демонстрацией...{Colors.END}")
            time.sleep(2)
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.GREEN}✅ Все демонстрации завершены!{Colors.END}\n")

def show_guide():
    """Показывает руководство"""
    guide_path = Path('DEMO_GUIDE.md')
    
    if not guide_path.exists():
        print(f"{Colors.RED}❌ Файл не найден: DEMO_GUIDE.md{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}📖 РУКОВОДСТВО ПО ДЕМОНСТРАЦИЯМ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    with open(guide_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(content)
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def check_requirements():
    """Проверяет наличие требуемых модулей"""
    print(f"{Colors.BOLD}{Colors.CYAN}Проверка требований...{Colors.END}\n")
    
    requirements = {
        'django': 'Django 6.0.1+',
        'celery': 'Celery (асинхронность)',
        'redis': 'Redis Python клиент',
    }
    
    missing = []
    for module, description in requirements.items():
        try:
            __import__(module)
            print(f"{Colors.GREEN}✓{Colors.END} {description}")
        except ImportError:
            print(f"{Colors.RED}✗{Colors.END} {description} (не установлен)")
            missing.append(module)
    
    if missing:
        print(f"\n{Colors.YELLOW}⚠️  Рекомендация:{Colors.END}")
        print(f"pip install {' '.join(missing)}\n")
    
    # Проверка Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print(f"{Colors.GREEN}✓{Colors.END} Redis (доступен)")
    except:
        print(f"{Colors.YELLOW}⚠️  Redis{Colors.END} (не доступен - используется LocMemCache)")
    
    print()

def main():
    print_banner()
    check_requirements()
    
    while True:
        print_menu()
        
        try:
            choice = input(f"{Colors.BOLD}{Colors.CYAN}Введите номер (0-5): {Colors.END}").strip()
            
            if choice == '0':
                print(f"\n{Colors.GREEN}✅ До свидания!{Colors.END}\n")
                break
            elif choice == '1':
                run_demo(1)
            elif choice == '2':
                run_demo(2)
            elif choice == '3':
                run_demo(3)
            elif choice == '4':
                run_all_demos()
            elif choice == '5':
                show_guide()
            else:
                print(f"\n{Colors.RED}❌ Неверный ввод. Выберите 0-5{Colors.END}\n")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏸️  Программа остановлена пользователем{Colors.END}\n")
            break
        except Exception as e:
            print(f"\n{Colors.RED}❌ Ошибка: {e}{Colors.END}\n")
        
        # Пауза перед меню
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"{Colors.RED}❌ Критическая ошибка: {e}{Colors.END}")
        sys.exit(1)
