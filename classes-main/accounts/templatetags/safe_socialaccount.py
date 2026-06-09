"""
Custom template tags for safe social account handling.
Handles MultipleObjectsReturned errors when multiple SocialApp entries exist.
"""
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def safe_provider_login_url(provider, process=None):
    """
    Safely get the provider login URL, handling MultipleObjectsReturned.
    Falls back to '#' if allauth is not configured or if multiple apps exist.
    """
    try:
        from allauth.socialaccount.models import SocialApp
    except ImportError:
        # allauth not installed
        return '#'
    
    try:
        # Try to get the app - if multiple exist, get the first one
        try:
            app = SocialApp.objects.get(provider=provider)
        except SocialApp.MultipleObjectsReturned:
            # Get the first one instead
            app = SocialApp.objects.filter(provider=provider).first()
            if not app:
                return '#'
        except SocialApp.DoesNotExist:
            return '#'
        
        # Construct the login URL - allauth expects this format for OAuth redirect
        login_url = f'/accounts/{provider}/login/'
        if process:
            login_url += f'?process={process}'
        
        return login_url
    except Exception:
        # Fallback on any error
        return '#'


@register.simple_tag
def safe_get_providers():
    """
    Safely get list of available providers, handling MultipleObjectsReturned.
    """
    try:
        from allauth.socialaccount.models import SocialApp
    except ImportError:
        return []
    
    try:
        # Get unique providers, handling multiple entries per provider
        providers = SocialApp.objects.values_list('provider', flat=True).distinct()
        return list(providers)
    except Exception:
        return []


@register.filter
def provider_display_name(provider):
    """Convert provider name to display name."""
    names = {
        'google': 'Google',
        'github': 'GitHub',
        'facebook': 'Facebook',
        'twitter': 'Twitter',
    }
    return names.get(provider, provider.title())
