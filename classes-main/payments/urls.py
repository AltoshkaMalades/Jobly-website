"""
Payment API URL routes.
"""
from django.urls import path
from . import views, kpi, dashboard_views

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
    
    # Payment pages
    path('paypal/', views.paypal_payment_page, name='paypal_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('error/', views.payment_error, name='payment_error'),
    
    # Payment dashboard
    path('history/', dashboard_views.payment_history, name='payment_history'),
    path('orders/<int:order_id>/', dashboard_views.order_details, name='order_details'),
    path('stats/', dashboard_views.payment_stats, name='payment_stats'),
    path('metrics/', dashboard_views.saas_metrics, name='saas_metrics'),
    
    # KPI Dashboard endpoints
    path('api/kpi/dashboard/', kpi.kpi_dashboard, name='kpi_dashboard'),
    path('api/kpi/revenue-by-date/', kpi.revenue_by_date, name='revenue_by_date'),
    path('api/kpi/conversion-funnel/', kpi.conversion_funnel, name='conversion_funnel'),
]
