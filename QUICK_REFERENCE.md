#!/bin/bash

# 🚀 БЫСТРЫЙ СПРАВОЧНИК: МИГРАЦИИ И ТЕСТЫ

# ============================================================================
# 1️⃣ КОМАНДЫ МИГРАЦИЙ (DJANGO)
# ============================================================================

echo "📚 КОМАНДЫ МИГРАЦИЙ:"
echo ""
echo "Создать новую миграцию:"
echo "  python manage.py makemigrations"
echo ""
echo "Применить все миграции:"
echo "  python manage.py migrate"
echo ""
echo "Применить миграции с подробным выводом:"
echo "  python manage.py migrate --verbosity 2"
echo ""
echo "Откатить последнюю миграцию:"
echo "  python manage.py migrate app_name 0001"
echo ""
echo "Показать список миграций:"
echo "  python manage.py showmigrations"
echo ""

# ============================================================================
# 2️⃣ ЗАПУСК ТЕСТОВ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================

echo "🧪 ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ:"
echo ""
echo "Все тесты производительности (с выводом времени):"
echo "  pytest tests/performance/test_cache_performance.py -s -v"
echo ""
echo "Только тесты главной страницы:"
echo "  pytest tests/performance/test_cache_performance.py::TestHomePagePerformance -s -v"
echo ""
echo "Только тесты поиска:"
echo "  pytest tests/performance/test_cache_performance.py::TestSearchPagePerformance -s -v"
echo ""
echo "Комплексный тест всех страниц:"
echo "  pytest tests/performance/test_cache_performance.py::TestApplicationPerformance -s -v"
echo ""
echo "Тест очистки кэша:"
echo "  pytest tests/performance/test_cache_performance.py::test_cache_clear_invalidates_cache -s"
echo ""
echo "Быстрый запуск (без подробного вывода):"
echo "  pytest tests/performance/test_cache_performance.py -q"
echo ""
echo "С остановкой на первой ошибке:"
echo "  pytest tests/performance/test_cache_performance.py -s -x"
echo ""

# ============================================================================
# 3️⃣ УПРАВЛЕНИЕ КЭШЕМ
# ============================================================================

echo "🧹 УПРАВЛЕНИЕ КЭШЕМ:"
echo ""
echo "Очистить весь кэш:"
echo "  python manage_cache.py clear"
echo ""
echo "Показать статистику кэша:"
echo "  python manage_cache.py stats"
echo ""
echo "Тест подключения Redis:"
echo "  python manage_cache.py test-redis"
echo ""

# ============================================================================
# 4️⃣ ЗАПУСК ВСЕХ ТЕСТОВ С ПОКРЫТИЕМ
# ============================================================================

echo "✅ ВСЕ ТЕСТЫ:"
echo ""
echo "Запустить все тесты с покрытием:"
echo "  pytest --cov=. --cov-report=html --cov-report=term-missing -v"
echo ""
echo "Только unit тесты:"
echo "  pytest tests/unit/ -v"
echo ""
echo "Только интеграционные тесты:"
echo "  pytest tests/integration/ -v"
echo ""
echo "Unit + Performance:"
echo "  pytest tests/unit/ tests/performance/ -v"
echo ""

# ============================================================================
# 5️⃣ GITHUB ACTIONS (CI/CD)
# ============================================================================

echo "🤖 GITHUB ACTIONS:"
echo ""
echo "GitHub Actions workflow файл:"
echo "  .github/workflows/deploy.yml"
echo ""
echo "При push в main ветку автоматически:"
echo "  1. Запускаются миграции (Django + Alembic)"
echo "  2. Запускаются тесты"
echo "  3. Если успешно - деплой на Render"
echo ""

# ============================================================================
# 6️⃣ RENDER (PRODUCTION DEPLOYMENT)
# ============================================================================

echo "🌐 RENDER DEPLOYMENT:"
echo ""
echo "Pre-deploy команда в Render (автоматические миграции):"
echo "  cd classes-main && python manage.py migrate --noinput"
echo ""
echo "Или используйте скрипт:"
echo "  bash scripts/render_predeploy.sh"
echo ""

# ============================================================================
# 7️⃣ ПОЛЕЗНЫЕ КОМАНДЫ
# ============================================================================

echo "🛠️  ПОЛЕЗНЫЕ КОМАНДЫ:"
echo ""
echo "Запустить Django shell (для отладки):"
echo "  python manage.py shell"
echo ""
echo "Создать superuser:"
echo "  python manage.py createsuperuser"
echo ""
echo "Собрать статические файлы:"
echo "  python manage.py collectstatic --noinput"
echo ""
echo "Проверить код на стиль (flake8):"
echo "  flake8 . --max-line-length=100"
echo ""
echo "Форматировать код (black):"
echo "  black ."
echo ""

# ============================================================================
# 8️⃣ БЫСТРЫЕ ПРИМЕРЫ
# ============================================================================

echo "⚡ БЫСТРЫЕ ПРИМЕРЫ:"
echo ""
echo "1. Создать и применить миграцию в один шаг:"
echo "   python manage.py makemigrations && python manage.py migrate"
echo ""
echo "2. Запустить тесты производительности кэша:"
echo "   pytest tests/performance/test_cache_performance.py -s"
echo ""
echo "3. Проверить, работает ли Redis:"
echo "   python manage_cache.py test-redis"
echo ""
echo "4. Запустить ВСЕ тесты:"
echo "   pytest"
echo ""
echo "5. Подготовить к деплою (как в Render):"
echo "   cd classes-main && python manage.py migrate --noinput && pytest tests/performance/ -v"
echo ""
