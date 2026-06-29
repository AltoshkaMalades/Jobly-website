from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'simulator_http_requests_total',
    'Total HTTP requests processed by the simulator application',
    ['method', 'endpoint', 'status'],
)

REQUEST_DURATION_SECONDS = Histogram(
    'simulator_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

REQUEST_EXCEPTIONS = Counter(
    'simulator_http_request_exceptions_total',
    'Total HTTP request exceptions raised by the simulator application',
    ['method', 'endpoint'],
)


def track_request(endpoint: str, method: str, status_code: int, duration_seconds: float) -> None:
    if not endpoint:
        endpoint = 'unknown'

    normalized_endpoint = endpoint if endpoint.startswith('/') else f'/{endpoint}'
    REQUEST_COUNT.labels(method=method, endpoint=normalized_endpoint, status=str(status_code)).inc()
    REQUEST_DURATION_SECONDS.labels(method=method, endpoint=normalized_endpoint).observe(duration_seconds)


def track_exception(endpoint: str, method: str) -> None:
    if not endpoint:
        endpoint = 'unknown'

    normalized_endpoint = endpoint if endpoint.startswith('/') else f'/{endpoint}'
    REQUEST_EXCEPTIONS.labels(method=method, endpoint=normalized_endpoint).inc()
