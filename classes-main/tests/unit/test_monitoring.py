import json
import logging
from unittest.mock import Mock, patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

from core import logging as core_logging
from core.middleware_metrics import PrometheusMetricsMiddleware
from core.views_metrics import metrics_view
from core import metrics as core_metrics


@pytest.mark.django_db
def test_metrics_view_returns_prometheus_payload(client):
    response = client.get(reverse('metrics'))

    assert response.status_code == 200
    assert 'text/plain' in response['Content-Type']
    body = response.content.decode('utf-8')
    assert 'simulator_http_requests_total' in body
    assert 'simulator_http_request_duration_seconds' in body


def test_track_request_records_counter_and_histogram(monkeypatch):
    counters = {}

    def make_counter(name, documentation, labelnames=None, buckets=None):
        if labelnames is None:
            labelnames = []
        return Mock(**{
            'labels.return_value.inc.return_value': None,
            'labels.return_value.observe.return_value': None,
        })

    monkeypatch.setattr(core_metrics, 'REQUEST_COUNT', Mock())
    monkeypatch.setattr(core_metrics, 'REQUEST_DURATION_SECONDS', Mock())

    core_metrics.track_request(endpoint='/hello', method='GET', status_code=200, duration_seconds=0.42)

    core_metrics.REQUEST_COUNT.labels.assert_called_once_with(method='GET', endpoint='/hello', status='200')
    core_metrics.REQUEST_DURATION_SECONDS.labels.assert_called_once_with(method='GET', endpoint='/hello')
    core_metrics.REQUEST_COUNT.labels.return_value.inc.assert_called_once()
    core_metrics.REQUEST_DURATION_SECONDS.labels.return_value.observe.assert_called_once_with(0.42)


def test_track_exception_records_counter(monkeypatch):
    monkeypatch.setattr(core_metrics, 'REQUEST_EXCEPTIONS', Mock())

    core_metrics.track_exception(endpoint='/error', method='POST')

    core_metrics.REQUEST_EXCEPTIONS.labels.assert_called_once_with(method='POST', endpoint='/error')
    core_metrics.REQUEST_EXCEPTIONS.labels.return_value.inc.assert_called_once()


def test_prometheus_metrics_middleware_calls_track_request(monkeypatch):
    request = RequestFactory().get('/some-path')
    response = HttpResponse('ok', status=200)
    middleware = PrometheusMetricsMiddleware(get_response=lambda req: response)

    track_request_mock = Mock()
    monkeypatch.setattr('core.middleware_metrics.track_request', track_request_mock)

    middleware.process_request(request)
    middleware.process_response(request, response)

    assert track_request_mock.called
    args, kwargs = track_request_mock.call_args
    assert kwargs['endpoint'] == '/some-path'
    assert kwargs['method'] == 'GET'
    assert kwargs['status_code'] == 200
    assert kwargs['duration_seconds'] >= 0.0


def test_prometheus_metrics_middleware_calls_track_exception(monkeypatch):
    request = RequestFactory().post('/broken')
    middleware = PrometheusMetricsMiddleware(get_response=lambda req: HttpResponse('fail', status=500))

    track_exception_mock = Mock()
    monkeypatch.setattr('core.middleware_metrics.track_exception', track_exception_mock)

    middleware.process_exception(request, RuntimeError('boom'))

    track_exception_mock.assert_called_once_with(endpoint='/broken', method='POST')


def test_request_context_filter_and_json_formatter():
    request = RequestFactory().get('/logged-path')
    request.user = Mock(is_authenticated=False, username='anonymous')

    core_logging.set_request_context(request)
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='test message',
        args=(),
        exc_info=None,
    )

    filter_ = core_logging.RequestContextFilter()
    assert filter_.filter(record)

    formatter = core_logging.JsonFormatter()
    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed['message'] == 'test message'
    assert parsed['path'] == '/logged-path'
    assert parsed['method'] == 'GET'
    assert parsed['user'] == 'anonymous'
    assert 'request_id' in parsed

    core_logging.clear_request_context()
    assert core_logging.get_request_context() == {}


def test_monitoring_dashboard_page_renders(client):
    response = client.get(reverse('monitoring-dashboard'))

    assert response.status_code == 200
    assert b'Monitoring Dashboard' in response.content
    assert b'Quick Links' in response.content


def test_monitoring_dashboard_api_endpoints_return_json(client):
    response_metrics = client.get(reverse('api-metrics'))
    response_health = client.get(reverse('api-health'))
    response_logs = client.get(reverse('api-logs'))

    assert response_metrics.status_code == 200
    assert response_metrics['Content-Type'].startswith('application/json')
    assert 'metrics' in response_metrics.json()

    assert response_health.status_code == 200
    assert response_health['Content-Type'].startswith('application/json')
    assert 'services' in response_health.json()

    assert response_logs.status_code == 200
    assert response_logs['Content-Type'].startswith('application/json')
    assert 'logs' in response_logs.json()


def test_monitoring_health_returns_unknown_when_urls_not_configured(settings, client):
    settings.PROMETHEUS_URL = ''
    settings.GRAFANA_URL = ''
    settings.PROMETHEUS_HEALTH_URL = ''
    settings.GRAFANA_HEALTH_URL = ''

    response = client.get(reverse('api-health'))
    data = response.json()

    assert response.status_code == 200
    assert data['services']['django']['status'] == 'up'
    assert data['services']['prometheus']['status'] == 'unknown'
    assert data['services']['grafana']['status'] == 'unknown'
    assert data['overall_status'] == 'healthy'
