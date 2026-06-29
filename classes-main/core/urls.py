"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import health_check
from accounts.views import home_page

urlpatterns = [
    # 1. Root home page
    path('', home_page, name='home'),
    # Expose accounts routes at root (tests expect endpoints like /register/, /login/ etc.)
    path('', include('accounts.urls')),
    
    # 2. Админка
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('metrics/', include('core.urls_metrics')),
    
    # 3. All accounts routes (login, register, profile, jobs, etc.) under /accounts/ prefix
    path('accounts/', include('accounts.urls')),
    
    # 4. Allauth for Google OAuth
    path('accounts/', include('allauth.urls')),
    
    # 5. Learning routes
    path('learning/', include('learning.urls')),
    
    # 6. Payment routes
    path('', include('payments.urls')),
]
    