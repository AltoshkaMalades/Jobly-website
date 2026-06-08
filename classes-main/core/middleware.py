"""
Security headers middleware for CSP and Permissions-Policy
"""


class SecurityHeadersMiddleware:
    """Добавляет Content-Security-Policy и Permissions-Policy заголовки для защиты от XSS и других атак."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content-Security-Policy: разрешает контент только с доверенных источников
        # Разрешены:
        # - 'self' - текущий домен (jobly.kz)
        # - 'unsafe-inline' для inline стилей и скриптов (необходимо для Tailwind)
        # - Google OAuth и reCAPTCHA
        # - CDN для шрифтов и иконок
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https://www.svgrepo.com https://*.googleusercontent.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "frame-src 'self' https://www.google.com https://recaptcha.net; "
            "connect-src 'self';"
        )
        
        # Permissions-Policy: ограничивает доступ браузера к API
        # Запрещаем: камеру, микрофон, геолокацию
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        return response
