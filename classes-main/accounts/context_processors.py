"""
Context processor to provide safe social account provider information to all templates.
Handles MultipleObjectsReturned errors gracefully.
"""
import os
from core.analytics import is_ga4_enabled, get_ga4_measurement_id


def social_providers(request):
    """
    Provide social account providers to all templates.
    Handles multiple SocialApp entries gracefully.
    """
    context = {
        'social_providers': [],
        'google_provider': None,
    }
    
    try:
        from allauth.socialaccount.models import SocialApp
    except ImportError:
        # allauth not installed
        return context
    
    try:
        # Try to get available providers
        apps = SocialApp.objects.all().distinct('provider')
        context['social_providers'] = list(apps.values_list('provider', flat=True))
        
        # Try to get Google provider (handle MultipleObjectsReturned)
        try:
            google_app = SocialApp.objects.filter(provider='google').first()
            if google_app:
                context['google_provider'] = google_app
        except Exception:
            # If multiple Google apps exist, just use the first one
            google_app = SocialApp.objects.filter(provider='google').first()
            if google_app:
                context['google_provider'] = google_app
    except Exception:
        # Silently handle any other errors
        pass
    
    return context


def ga4_context(request):
    """
    Add Google Analytics 4 configuration to template context.
    """
    return {
        'GA4_ENABLED': is_ga4_enabled(),
        'GA4_MEASUREMENT_ID': get_ga4_measurement_id(),
    }
