import json
import logging
import threading
import uuid
from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def set_request_context(request):
    request_id = request.META.get('HTTP_X_REQUEST_ID') or str(uuid.uuid4())
    _thread_locals.request_context = {
        'path': request.path,
        'method': request.method,
        'user': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
        'request_id': request_id,
    }


def get_request_context():
    return getattr(_thread_locals, 'request_context', {})


def clear_request_context():
    _thread_locals.request_context = {}


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = get_request_context()
        record.request_id = context.get('request_id')
        record.user = context.get('user')
        record.path = context.get('path')
        record.method = context.get('method')
        return True


class RequestContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_request_context(request)

    def process_response(self, request, response):
        clear_request_context()
        return response

    def process_exception(self, request, exception):
        clear_request_context()
        return None


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        payload = {
            'timestamp': timestamp,
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName,
            'line': record.lineno,
        }

        if getattr(record, 'request_id', None):
            payload['request_id'] = record.request_id

        if getattr(record, 'user', None):
            payload['user'] = record.user

        if getattr(record, 'path', None):
            payload['path'] = record.path

        if getattr(record, 'method', None):
            payload['method'] = record.method

        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)
