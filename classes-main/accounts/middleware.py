import logging
import re
from django.core.cache import cache
from django.http import HttpResponse

logger = logging.getLogger(__name__)

RATE_LIMIT_KEY_PREFIX = 'rl'
RATE_LIMIT_MAX_ATTEMPTS = 5
RATE_LIMIT_WINDOW_SECONDS = 5 * 60
RATE_LIMIT_PATH_PATTERNS = [
    re.compile(r'^/login/$'),
    re.compile(r'^/register/$'),
    re.compile(r'^/password-reset/$'),
    re.compile(r'^/password-reset-confirm/.+/.*$'),
    re.compile(r'^/job/\d+/apply/$'),
]


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


class EndpointRateLimitMiddleware:
    """Very lightweight rate limiter for critical POST endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def _is_protected_path(self, path):
        return any(pattern.match(path) for pattern in RATE_LIMIT_PATH_PATTERNS)

    def _build_cache_key(self, path, client_ip):
        return f"{RATE_LIMIT_KEY_PREFIX}:{client_ip}:{path}"

    def __call__(self, request):
        if request.method == 'POST' and self._is_protected_path(request.path):
            client_ip = get_client_ip(request)
            cache_key = self._build_cache_key(request.path, client_ip)
            try:
                attempts = cache.get(cache_key, 0)
            except Exception as exc:
                logger.warning(
                    'Rate limit cache unavailable, bypassing cache check: %s',
                    exc,
                )
                return self.get_response(request)

            if attempts >= RATE_LIMIT_MAX_ATTEMPTS:
                return HttpResponse(
                    'Too Many Requests. Please wait a little and try again.',
                    status=429,
                )

            response = self.get_response(request)

            try:
                if response.status_code == 302:
                    cache.delete(cache_key)
                else:
                    cache.set(cache_key, attempts + 1, RATE_LIMIT_WINDOW_SECONDS)
            except Exception as exc:
                logger.warning(
                    'Failed to update rate limit cache; continuing without cache: %s',
                    exc,
                )

            return response

        return self.get_response(request)
