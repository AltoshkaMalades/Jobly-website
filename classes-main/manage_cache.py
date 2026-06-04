#!/usr/bin/env python
"""
manage_cache.py - Утилита для управления кэшем в приложении

Использование:
    python manage_cache.py clear           # Очистить весь кэш
    python manage_cache.py stats           # Показать статистику кэша
    python manage_cache.py test_redis      # Тест подключения Redis
"""

import os
import sys
import django

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.cache import caches, cache
from django.core.management.base import BaseCommand
import redis


def clear_cache():
    """Очищает весь кэш."""
    try:
        cache.clear()
        print("✅ Кэш успешно очищен")
        return True
    except Exception as e:
        print(f"❌ Ошибка при очистке кэша: {e}")
        return False


def get_cache_stats():
    """Показывает статистику кэша."""
    try:
        from django.conf import settings
        
        print("\n📊 ИНФОРМАЦИЯ О КЭШЕ:\n")
        
        backend = settings.CACHES['default']['BACKEND']
        print(f"Backend: {backend}")
        
        if 'redis' in backend.lower():
            print(f"Location: {settings.CACHES['default']['LOCATION']}")
            
            # Подключаемся к Redis для статистики
            try:
                redis_url = settings.CACHES['default']['LOCATION']
                r = redis.from_url(redis_url)
                
                info = r.info()
                print(f"\nRedis статистика:")
                print(f"  - Connected: ✅")
                print(f"  - Memory used: {info.get('used_memory_human', 'N/A')}")
                print(f"  - Number of keys: {r.dbsize()}")
                print(f"  - Version: {info.get('redis_version', 'N/A')}")
                
                # Список ключей (для дебага)
                keys = r.keys('*')[:10]  # Первые 10 ключей
                if keys:
                    print(f"\n📍 Примеры ключей кэша:")
                    for key in keys:
                        ttl = r.ttl(key)
                        ttl_str = f"{ttl}s" if ttl > 0 else "no expiry"
                        print(f"   - {key.decode() if isinstance(key, bytes) else key} ({ttl_str})")
            
            except Exception as e:
                print(f"  - Error: {e}")
        
        elif 'locmem' in backend.lower():
            print("Location: Local Memory (LocMemCache)")
            print("⚠️  Local memory cache потеряется при перезагрузке приложения")
        
        elif 'sqlite' in backend.lower():
            print("Location: SQLite")
        
        print()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def test_redis_connection():
    """Тестирует подключение к Redis."""
    try:
        from django.conf import settings
        
        print("\n🔍 ТЕСТИРОВАНИЕ REDIS:\n")
        
        redis_url = settings.CACHES['default'].get('LOCATION')
        
        if not redis_url:
            print("❌ Redis URL не найден в settings")
            return False
        
        print(f"URL: {redis_url}")
        
        try:
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Подключение успешно!")
            
            # Тест записи/чтения
            test_key = 'test_key_django'
            test_value = 'test_value_12345'
            
            r.set(test_key, test_value, ex=10)
            retrieved = r.get(test_key).decode()
            
            if retrieved == test_value:
                print(f"✅ Запись/чтение работает")
                r.delete(test_key)
                print(f"✅ Удаление ключей работает")
                return True
            else:
                print(f"❌ Значение не совпадает: {retrieved} != {test_value}")
                return False
        
        except redis.ConnectionError as e:
            print(f"❌ Redis не доступен: {e}")
            print(f"   Убедитесь, что Redis запущен и доступен по адресу {redis_url}")
            return False
        
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        return False


def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("""
Утилита для управления кэшем в Django приложении.

Команды:
    clear       - Очистить весь кэш
    stats       - Показать статистику кэша
    test-redis  - Тест подключения Redis

Примеры:
    python manage_cache.py clear
    python manage_cache.py stats
    python manage_cache.py test-redis
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'clear':
        clear_cache()
    elif command == 'stats':
        get_cache_stats()
    elif command in ['test-redis', 'test_redis']:
        test_redis_connection()
    else:
        print(f"❌ Неизвестная команда: {command}")


if __name__ == '__main__':
    main()
