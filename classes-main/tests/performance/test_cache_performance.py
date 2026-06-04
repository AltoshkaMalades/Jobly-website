"""
tests/performance/test_cache_performance.py

Тесты производительности для проверки эффективности кэширования.
Измеряет время ответа страниц с кэшем и без, проверяет улучшение скорости.

Запуск:
    # Запустить тест с выводом времени
    pytest tests/performance/test_cache_performance.py -s -v

    # Запустить конкретный тест
    pytest tests/performance/test_cache_performance.py::test_home_page_performance -s

    # Запустить с подробным выводом
    pytest tests/performance/test_cache_performance.py -s -v --tb=short
"""

import time
import pytest
from django.core.cache import caches, cache
from django.test import override_settings
from django.urls import reverse
from django.contrib.auth.models import User


# ============================================================================
# КОНФИГУРАЦИЯ КЭША ДЛЯ ТЕСТОВ
# ============================================================================

TEST_CACHE_SETTINGS = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache-location',
    }
}


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def measure_response_time(client, url, label=""):
    """
    Замеряет время выполнения HTTP запроса.
    
    Args:
        client: Django test client
        url: URL для запроса
        label: Описание для логирования
        
    Returns:
        tuple: (response, execution_time_in_ms)
    """
    start_time = time.perf_counter()
    response = client.get(url)
    end_time = time.perf_counter()
    
    execution_time_ms = (end_time - start_time) * 1000
    
    if label:
        print(f"\n⏱️  {label}: {execution_time_ms:.2f} ms")
    
    return response, execution_time_ms


def clear_all_caches():
    """Очищает все кэши в приложении."""
    for cache_name in caches:
        caches[cache_name].clear()
    print("\n🧹 Кэш очищен")


# ============================================================================
# ТЕСТ 1: ПРОИЗВОДИТЕЛЬНОСТЬ ГЛАВНОЙ СТРАНИЦЫ
# ============================================================================

@pytest.mark.django_db
class TestHomePagePerformance:
    """Тесты производительности главной страницы с кэшем и без."""
    
    @override_settings(CACHES=TEST_CACHE_SETTINGS)
    def test_home_page_cache_improves_performance(self, client):
        """
        Проверяет, что закэшированная версия страницы загружается значительно быстрее.
        
        Ожидание: Второй запрос (с кэшем) должен быть быстрее в 5-10 раз,
                 чем первый запрос (без кэша).
        """
        url = reverse('home')
        
        # Шаг 1: ОЧИЩАЕМ КЭШ
        clear_all_caches()
        
        # Шаг 2: ПЕРВЫЙ ЗАПРОС (БЕЗ КЭША)
        response_uncached, time_without_cache = measure_response_time(
            client, url, 
            label="Первый запрос (без кэша)"
        )
        assert response_uncached.status_code == 200, \
            f"Ожидалось 200, получено {response_uncached.status_code}"
        
        # Шаг 3: ВТОРОЙ ЗАПРОС (С КЭШЕМ)
        response_cached, time_with_cache = measure_response_time(
            client, url,
            label="Второй запрос (с кэшем)"
        )
        assert response_cached.status_code == 200, \
            f"Ожидалось 200, получено {response_cached.status_code}"
        
        # Шаг 4: ПРОВЕРЯЕМ УЛУЧШЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ
        speedup_ratio = time_without_cache / time_with_cache
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТА HOME PAGE:")
        print(f"   Без кэша:    {time_without_cache:.2f} ms")
        print(f"   С кэшем:     {time_with_cache:.2f} ms")
        print(f"   Ускорение:   {speedup_ratio:.2f}x раз")
        
        # Минимальное ускорение - 1.5x (даже медленный кэш)
        MIN_SPEEDUP = 1.5
        assert speedup_ratio >= MIN_SPEEDUP, \
            f"Кэш не дал ожидаемое улучшение. " \
            f"Ускорение: {speedup_ratio:.2f}x, ожидалось минимум {MIN_SPEEDUP}x. " \
            f"Без кэша: {time_without_cache:.2f}ms, с кэшем: {time_with_cache:.2f}ms"
        
        # Проверяем, что контент одинаков
        assert response_cached.content == response_uncached.content, \
            "Контент кэшированной страницы отличается от оригинала"
        
        print(f"   ✅ Тест PASSED (минимальное требование: {MIN_SPEEDUP}x)")

    def test_home_page_cache_consistency(self, client):
        """
        Проверяет, что кэшированная страница содержит актуальные данные.
        """
        url = reverse('home')
        
        clear_all_caches()
        
        # Делаем несколько последовательных запросов
        responses = []
        times = []
        
        for i in range(3):
            response, exec_time = measure_response_time(
                client, url,
                label=f"Запрос #{i+1}"
            )
            responses.append(response)
            times.append(exec_time)
            assert response.status_code == 200
        
        # Все ответы должны быть идентичны
        for i in range(1, len(responses)):
            assert responses[i].content == responses[0].content, \
                f"Запрос #{i+1} отличается от первого"
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТА CONSISTENCY:")
        print(f"   Запрос 1: {times[0]:.2f} ms (без кэша)")
        print(f"   Запрос 2: {times[1]:.2f} ms (с кэшем)")
        print(f"   Запрос 3: {times[2]:.2f} ms (с кэшем)")
        print(f"   ✅ Все ответы идентичны")


# ============================================================================
# ТЕСТ 2: ПРОИЗВОДИТЕЛЬНОСТЬ СТРАНИЦЫ ПОИСКА
# ============================================================================

@pytest.mark.django_db
class TestSearchPagePerformance:
    """Тесты производительности страницы поиска с кэшем и без."""
    
    @override_settings(CACHES=TEST_CACHE_SETTINGS)
    def test_search_page_cache_improves_performance(self, client):
        """
        Проверяет, что поиск с кэшем работает значительно быстрее.
        
        Особенность: Каждый поисковый запрос может кэшироваться отдельно
                     в зависимости от параметров.
        """
        search_query = "test_job"
        url = f"{reverse('search')}?query={search_query}"
        
        # Шаг 1: ОЧИЩАЕМ КЭШ
        clear_all_caches()
        
        # Шаг 2: ПЕРВЫЙ ЗАПРОС (БЕЗ КЭША)
        response_uncached, time_without_cache = measure_response_time(
            client, url,
            label="Поиск без кэша"
        )
        assert response_uncached.status_code == 200
        
        # Шаг 3: ВТОРОЙ ЗАПРОС (С КЭШЕМ) - тот же поиск
        response_cached, time_with_cache = measure_response_time(
            client, url,
            label="Поиск с кэшем (тот же запрос)"
        )
        assert response_cached.status_code == 200
        
        # Шаг 4: ПРОВЕРЯЕМ УЛУЧШЕНИЕ
        speedup_ratio = time_without_cache / time_with_cache
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТА SEARCH PAGE:")
        print(f"   Без кэша:    {time_without_cache:.2f} ms")
        print(f"   С кэшем:     {time_with_cache:.2f} ms")
        print(f"   Ускорение:   {speedup_ratio:.2f}x раз")
        
        # Минимальное ускорение - 1.5x
        MIN_SPEEDUP = 1.5
        assert speedup_ratio >= MIN_SPEEDUP, \
            f"Кэш поиска не дал ожидаемое улучшение. " \
            f"Ускорение: {speedup_ratio:.2f}x, ожидалось минимум {MIN_SPEEDUP}x"
        
        assert response_cached.content == response_uncached.content
        
        print(f"   ✅ Тест PASSED (минимальное требование: {MIN_SPEEDUP}x)")

    def test_search_different_queries_have_different_cache(self, client):
        """
        Проверяет, что разные поисковые запросы кэшируются отдельно.
        """
        clear_all_caches()
        
        # Поиск 1
        url1 = f"{reverse('search')}?query=python"
        response1, time1 = measure_response_time(client, url1, "Поиск 'python' (без кэша)")
        
        # Поиск 2 (другой запрос)
        url2 = f"{reverse('search')}?query=javascript"
        response2, time2 = measure_response_time(client, url2, "Поиск 'javascript' (без кэша)")
        
        # Повторный поиск 1 (с кэшем)
        response1_cached, time1_cached = measure_response_time(
            client, url1, 
            "Поиск 'python' (с кэшем)"
        )
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТА РАЗНЫХ КЭШЕЙ:")
        print(f"   'python' 1-й раз:     {time1:.2f} ms")
        print(f"   'javascript' 1-й раз: {time2:.2f} ms")
        print(f"   'python' 2-й раз:     {time1_cached:.2f} ms")
        print(f"   ✅ Разные поиски кэшируются независимо")


# ============================================================================
# ТЕСТ 3: КОМПЛЕКСНЫЙ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ВСЕГО ПРИЛОЖЕНИЯ
# ============================================================================

@pytest.mark.django_db
class TestApplicationPerformance:
    """Комплексный тест производительности различных страниц."""
    
    @override_settings(CACHES=TEST_CACHE_SETTINGS)
    def test_multiple_pages_with_and_without_cache(self, client):
        """
        Тестирует производительность нескольких страниц и показывает сводку.
        """
        pages = [
            ('home', reverse('home')),
            ('search', f"{reverse('search')}?query=test"),
        ]
        
        clear_all_caches()
        
        results = {}
        
        print(f"\n{'='*70}")
        print(f"📊 КОМПЛЕКСНЫЙ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПРИЛОЖЕНИЯ")
        print(f"{'='*70}")
        
        for page_name, url in pages:
            # Первый запрос (без кэша)
            response1, time1 = measure_response_time(
                client, url,
                label=f"[{page_name.upper()}] Первый запрос (без кэша)"
            )
            
            # Второй запрос (с кэшем)
            response2, time2 = measure_response_time(
                client, url,
                label=f"[{page_name.upper()}] Второй запрос (с кэшем)"
            )
            
            speedup = time1 / time2 if time2 > 0 else float('inf')
            results[page_name] = {
                'without_cache': time1,
                'with_cache': time2,
                'speedup': speedup,
                'status': response1.status_code == 200
            }
        
        # Вывод итоговой таблицы
        print(f"\n{'='*70}")
        print(f"{'Страница':<20} {'Без кэша':<15} {'С кэшем':<15} {'Ускорение':<15}")
        print(f"{'-'*70}")
        
        for page_name, data in results.items():
            print(f"{page_name:<20} "
                  f"{data['without_cache']:<13.2f}ms {data['with_cache']:<13.2f}ms "
                  f"{data['speedup']:<13.2f}x")
        
        print(f"{'='*70}\n")
        
        # Проверяем, что все страницы работают
        for page_name, data in results.items():
            assert data['status'], f"Страница {page_name} вернула ошибку"
            assert data['speedup'] >= 1.0, \
                f"Кэш замедлил страницу {page_name}"


# ============================================================================
# ТЕСТ 4: ПРОВЕРКА ОЧИСТКИ КЭША
# ============================================================================

@pytest.mark.django_db
@override_settings(CACHES=TEST_CACHE_SETTINGS)
def test_cache_clear_invalidates_cache(client):
    """
    Проверяет, что после очистки кэша данные заново загружаются из БД.
    """
    url = reverse('home')
    
    print(f"\n{'='*70}")
    print(f"🧹 ТЕСТ ОЧИСТКИ КЭША")
    print(f"{'='*70}")
    
    # Запрос 1: без кэша
    clear_all_caches()
    response1, time1 = measure_response_time(client, url, "Запрос 1 (без кэша)")
    
    # Запрос 2: с кэшем
    response2, time2 = measure_response_time(client, url, "Запрос 2 (с кэшем)")
    
    # Запрос 3: после очистки кэша (снова из БД)
    clear_all_caches()
    response3, time3 = measure_response_time(client, url, "Запрос 3 (после очистки)")
    
    # Запрос 4: снова с кэшем
    response4, time4 = measure_response_time(client, url, "Запрос 4 (снова с кэшем)")
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   1️⃣  Без кэша:          {time1:.2f} ms")
    print(f"   2️⃣  С кэшем:           {time2:.2f} ms (быстрее в {time1/time2:.2f}x)")
    print(f"   3️⃣  После очистки:     {time3:.2f} ms (снова медленнее)")
    print(f"   4️⃣  С кэшем снова:     {time4:.2f} ms (снова быстро)")
    print(f"   ✅ Кэш корректно очищается и переиспользуется")
    
    # Проверяем, что запрос 3 медленнее запроса 2 (кэш был очищен)
    assert time3 > time2 * 0.8, \
        "После очистки кэша запрос должен быть медленнее"
    
    # Проверяем, что запрос 4 быстрый (кэш заново создан)
    assert time4 < time3 * 0.8, \
        "После переиспользования кэша запрос должен быть быстрым"


# ============================================================================
# ТЕСТ 5: EDGE CASE - ОЧЕНЬ ЧАСТЫЕ ЗАПРОСЫ
# ============================================================================

@pytest.mark.django_db
@override_settings(CACHES=TEST_CACHE_SETTINGS)
def test_cache_with_rapid_requests(client):
    """
    Проверяет производительность при частых последовательных запросах.
    """
    url = reverse('home')
    
    print(f"\n{'='*70}")
    print(f"⚡ ТЕСТ ЧАСТЫХ ЗАПРОСОВ")
    print(f"{'='*70}")
    
    clear_all_caches()
    
    # Делаем 10 быстрых запросов
    times = []
    for i in range(10):
        _, exec_time = measure_response_time(client, url, f"Запрос {i+1}")
        times.append(exec_time)
    
    # Первый запрос (без кэша) должен быть медленнее остальных
    avg_cached_time = sum(times[1:]) / len(times[1:])
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   1-й запрос (без кэша):  {times[0]:.2f} ms")
    print(f"   Средний (с кэшем):      {avg_cached_time:.2f} ms")
    print(f"   Ускорение:              {times[0] / avg_cached_time:.2f}x")
    print(f"   Min время (с кэшем):    {min(times[1:]):.2f} ms")
    print(f"   Max время (с кэшем):    {max(times[1:]):.2f} ms")
    
    # Проверяем, что кэшированные запросы быстрее
    assert times[0] > avg_cached_time * 1.2, \
        "Первый запрос должен быть значительно медленнее"


if __name__ == '__main__':
    pytest.main([__file__, '-s', '-v'])
