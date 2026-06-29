import logging
import time
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .metrics import track_request, track_exception

logger = logging.getLogger(__name__)


class PrometheusMetricsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._simulator_metrics_start = time.perf_counter()

    def process_response(self, request, response):
        start = getattr(request, '_simulator_metrics_start', None)
        duration = time.perf_counter() - start if start is not None else 0.0
        endpoint = request.path
        method = request.method

        try:
            track_request(endpoint=endpoint, method=method, status_code=response.status_code, duration_seconds=duration)
        except Exception as exc:
            logger.exception('Failed to record Prometheus metrics')

        return response

    def process_exception(self, request, exception):
        endpoint = request.path
        method = request.method
        try:
            track_exception(endpoint=endpoint, method=method)
        except Exception as exc:
            logger.exception('Failed to record Prometheus exception metric')
        return None
