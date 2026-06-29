from django.urls import path
from .views_metrics import metrics_view

urlpatterns = [
    path('', metrics_view, name='metrics'),
]
