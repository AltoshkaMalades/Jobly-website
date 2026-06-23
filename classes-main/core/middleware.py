"""
Security headers middleware for CSP and Permissions-Policy
"""


class SecurityHeadersMiddleware:
    """Добавляет Content-Security-Policy и Permissions-Policy заголовки для защиты от XSS и других атак."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content-Security-Policy: открытая политика для разработки
        # Разрешены все источники для локальной разработки, Tailwind и внешних ресурсов
        response['Content-Security-Policy'] = (
            "default-src 'self' *; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google.com https://www.gstatic.com https://www.googletagmanager.com https://cdn.tailwindcss.com https://www.paypal.com https://www.sandbox.paypal.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.tailwindcss.com; "
            "img-src 'self' data: https://www.svgrepo.com https://*.googleusercontent.com *; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "frame-src 'self' https://www.google.com https://recaptcha.net https://www.paypal.com https://www.sandbox.paypal.com https://sandbox.paypal.com; "
            "connect-src 'self' https://www.google-analytics.com https://www.googletagmanager.com *;"
        )
        
        # Permissions-Policy: ограничивает доступ браузера к API
        # Запрещаем: камеру, микрофон, геолокацию
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        # Strict-Transport-Security (HSTS): рекомендовано для HTTPS-сайтов
        # Браузеры игнорируют этот заголовок при соединениях по HTTP,
        # поэтому установка безопасна для разработки и обязательна для продакшна.
        response.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        
        return response
