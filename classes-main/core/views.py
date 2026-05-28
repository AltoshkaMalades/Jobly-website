import logging

from django.core.cache import caches
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

@require_GET
def health_check(request):
    result = {'status': 'ok', 'database': 'ok', 'cache': 'ok'}
    status_code = 200

    try:
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception as exc:
        logger.exception('Database health check failed')
        result['database'] = 'error'
        result['database_error'] = str(exc)
        status_code = 500

    try:
        cache = caches['default']
        cache.set('health_check_key', 'ok', timeout=5)
        if cache.get('health_check_key') != 'ok':
            raise RuntimeError('Cache read/write mismatch')
    except Exception as exc:
        logger.exception('Cache health check failed')
        result['cache'] = 'error'
        result['cache_error'] = str(exc)
        status_code = 500

    return JsonResponse(result, status=status_code)
