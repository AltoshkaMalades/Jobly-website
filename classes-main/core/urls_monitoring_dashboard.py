"""
URL routing for monitoring dashboard
"""
from django.urls import path
from .views_monitoring_dashboard import (
    monitoring_dashboard,
    api_metrics_summary,
    api_health_status,
    api_logs_recent,
)

urlpatterns = [
    # Main dashboard page
    path('', monitoring_dashboard, name='monitoring-dashboard'),
    
    # API endpoints for dashboard data
    path('api/metrics/', api_metrics_summary, name='api-metrics'),
    path('api/health/', api_health_status, name='api-health'),
    path('api/logs/', api_logs_recent, name='api-logs'),
]
