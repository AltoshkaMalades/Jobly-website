"""
Custom OAuth URL handlers that wrap allauth's views to handle MultipleObjectsReturned.
This approach intercepts requests before they reach allauth's problematic code.
"""
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


def get_safe_google_app():
    """Get Google SocialApp, handling MultipleObjectsReturned."""
    try:
        try:
            site = Site.objects.get_current()
        except:
            site = Site.objects.get(id=1)
        
        # Try to get app for current site first
        try:
            app = SocialApp.objects.get(provider='google', sites=site)
            return app
        except SocialApp.MultipleObjectsReturned:
            logger.warning("Multiple Google SocialApps for current site, using fallback")
        except SocialApp.DoesNotExist:
            pass
        
        # Fallback: get most recent Google app
        apps = SocialApp.objects.filter(provider='google').order_by('-id')
        if apps.exists():
            app = apps.first()
            logger.info(f"Using Google app {app.id} as fallback")
            return app
        
        raise SocialApp.DoesNotExist("No Google SocialApp found")
    
    except Exception as e:
        logger.error(f"Error getting safe Google app: {e}", exc_info=True)
        raise


def google_login_view(request):
    """
    Custom Google login view that handles MultipleObjectsReturned.
    This wraps allauth's OAuth flow to provide error handling.
    """
    try:
        process = request.GET.get('process', 'login')
        
        # Ensure we have a valid Google app in the database
        try:
            app = get_safe_google_app()
        except Exception as e:
            logger.error(f"Failed to get Google app: {e}")
            return JsonResponse({'error': 'Google authentication not configured'}, status=500)
        
        # Import and call allauth's view
        from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
        from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter, GoogleOAuth2View
        
        # Create the view
        view = GoogleOAuth2View()
        
        # Set up the view attributes
        view.request = request
        view.kwargs = {'process': process}
        view.adapter = GoogleOAuth2Adapter(request)
        
        # Call the dispatch method
        return view.dispatch(request, *[], **{'process': process})
    
    except SocialApp.MultipleObjectsReturned:
        logger.error("MultipleObjectsReturned in google_login_view - this should not happen with get_safe_google_app")
        return JsonResponse({'error': 'Multiple Google apps configured, please contact support'}, status=500)
    except Exception as e:
        logger.error(f"Error in google_login_view: {type(e).__name__}: {e}", exc_info=True)
        raise


def google_callback_view(request):
    """
    Custom Google callback view that handles MultipleObjectsReturned.
    """
    try:
        # Ensure we have a valid Google app
        try:
            app = get_safe_google_app()
        except Exception as e:
            logger.error(f"Failed to get Google app in callback: {e}")
            return JsonResponse({'error': 'Google authentication not configured'}, status=500)
        
        # Import and call allauth's callback view
        from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter, GoogleOAuth2CallbackView
        
        # Create the view
        view = GoogleOAuth2CallbackView()
        
        # Set up the view attributes
        view.request = request
        view.adapter = GoogleOAuth2Adapter(request)
        
        # Call the dispatch method
        return view.dispatch(request)
    
    except SocialApp.MultipleObjectsReturned:
        logger.error("MultipleObjectsReturned in google_callback_view")
        return JsonResponse({'error': 'Multiple Google apps configured, please contact support'}, status=500)
    except Exception as e:
        logger.error(f"Error in google_callback_view: {type(e).__name__}: {e}", exc_info=True)
        raise
