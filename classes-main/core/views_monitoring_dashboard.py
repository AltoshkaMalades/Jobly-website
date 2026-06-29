"""
Monitoring Dashboard - единая страница со всеми метриками и статусом сервисов
"""
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@require_GET
def monitoring_dashboard(request):
    """
    Основная страница мониторинга со всеми новыми функциями
    """
    context = {
        'title': 'Monitoring Dashboard',
        'current_time': datetime.now().isoformat(),
    }
    return render(request, 'monitoring_dashboard.html', context)


@require_GET
def api_metrics_summary(request):
    """
    API endpoint для получения сводки метрик в JSON
    """
    try:
        from prometheus_client import CollectorRegistry, generate_latest
        from core.metrics import REQUEST_COUNT, REQUEST_DURATION_SECONDS, REQUEST_EXCEPTIONS
        
        # Собрать текущие значения метрик
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': check_database_health(),
                'redis': check_redis_health(),
            },
            'metrics': {
                'total_requests': get_counter_value(REQUEST_COUNT),
                'request_duration_avg': get_histogram_average(REQUEST_DURATION_SECONDS),
                'request_exceptions': get_counter_value(REQUEST_EXCEPTIONS),
            },
            'endpoints': get_endpoint_metrics(),
        }
        return JsonResponse(metrics_data)
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def api_health_status(request):
    """
    Проверить статус всех компонентов системы
    """
    import subprocess
    
    health = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'overall_status': 'healthy',
    }
    
    # Проверить Django
    health['services']['django'] = {
        'status': 'up',
        'url': 'http://localhost:8000',
    }
    
    # Проверить Prometheus (если в Docker)
    health['services']['prometheus'] = {
        'status': check_service_status('http://localhost:9090/-/healthy'),
        'url': 'http://localhost:9090',
    }
    
    # Проверить Grafana (если в Docker)
    health['services']['grafana'] = {
        'status': check_service_status('http://localhost:3000/api/health'),
        'url': 'http://localhost:3000',
    }
    
    # Определить общий статус
    if any(s.get('status') == 'down' for s in health['services'].values()):
        health['overall_status'] = 'degraded'
    
    return JsonResponse(health)


@require_GET
def api_logs_recent(request):
    """
    Получить последние JSON логи
    """
    try:
        import os
        log_file = os.path.join(os.path.dirname(__file__), '..', 'debug.json.log')
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Последние 50 логов
                for line in lines[-50:]:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        
        return JsonResponse({'logs': logs[::-1]})  # Новые логи сверху
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# ============ Вспомогательные функции ============

def check_database_health():
    """Проверить здоровье БД"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return 'up'
    except Exception:
        return 'down'


def check_redis_health():
    """Проверить здоровье Redis"""
    try:
        import redis
        from django.conf import settings
        r = redis.from_url(settings.CACHES['default']['LOCATION'])
        r.ping()
        return 'up'
    except Exception:
        return 'down'


def check_service_status(url):
    """Проверить доступность сервиса"""
    try:
        import requests
        response = requests.get(url, timeout=2)
        return 'up' if response.status_code < 500 else 'down'
    except Exception:
        return 'down'


def get_counter_value(counter):
    """Получить значение счетчика Prometheus"""
    try:
        # Получить текущее значение из метрики
        return counter._value.get()
    except Exception:
        return 0


def get_histogram_average(histogram):
    """Получить среднее значение из гистограммы"""
    try:
        # Примерный расчет среднего
        sum_value = histogram._sum.get()
        count = histogram._created.get() or 1
        return sum_value / count if count > 0 else 0
    except Exception:
        return 0


def get_endpoint_metrics():
    """Получить метрики по эндпоинтам"""
    try:
        from core.metrics import REQUEST_COUNT
        
        endpoints = {}
        # Для каждой метрики в счетчике
        for sample in REQUEST_COUNT.collect()[0].samples:
            if sample.name == 'simulator_http_requests_total':
                labels = sample.labels
                endpoint = labels.get('endpoint', 'unknown')
                method = labels.get('method', 'unknown')
                status = labels.get('status', 'unknown')
                
                key = f"{method} {endpoint}"
                if key not in endpoints:
                    endpoints[key] = {
                        'total': 0,
                        'by_status': {},
                    }
                
                endpoints[key]['total'] += sample.value
                endpoints[key]['by_status'][status] = sample.value
        
        return endpoints
    except Exception:
        return {}
