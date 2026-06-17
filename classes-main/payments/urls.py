"""
Payment API URL routes.
"""
from django.urls import path
from . import views, kpi

app_name = 'payments'

urlpatterns = [
    # Payment endpoints
    path('api/payments/create/', views.create_payment, name='create_payment'),
    path('api/payments/orders/<int:order_id>/', views.get_order_status, name='get_order_status'),
    path('api/payments/transactions/<str:transaction_id>/', views.get_transaction_status, name='get_transaction_status'),
    path('api/payments/transactions/<str:transaction_id>/refund', views.refund_payment, name='refund_payment'),
    
    # Webhook endpoints
    path('api/payments/webhook/bereke', views.webhook_bereke, name='webhook_bereke'),
    path('api/payments/webhook/paypal', views.webhook_paypal, name='webhook_paypal'),
    
    # KPI Dashboard endpoints
    path('api/kpi/dashboard/', kpi.kpi_dashboard, name='kpi_dashboard'),
    path('api/kpi/revenue-by-date/', kpi.revenue_by_date, name='revenue_by_date'),
    path('api/kpi/conversion-funnel/', kpi.conversion_funnel, name='conversion_funnel'),
]
