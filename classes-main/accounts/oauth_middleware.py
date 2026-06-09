"""
Middleware for handling MultipleObjectsReturned errors from allauth.
This is a last-resort error handler for any MultipleObjectsReturned errors.
"""
import logging
from django.http import JsonResponse, HttpResponseRedirect

logger = logging.getLogger(__name__)


class SocialAppDuplicateHandlerMiddleware:
    """
    Catches MultipleObjectsReturned errors from allauth OAuth flows
    and redirects to cleanup or a friendly error page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Check if this is a MultipleObjectsReturned error from allauth
            error_name = type(e).__name__
            if 'MultipleObjectsReturned' in error_name:
                logger.error(
                    f"MultipleObjectsReturned error caught in middleware at {request.path}: {str(e)}",
                    exc_info=True
                )
                
                # Try to cleanup duplicates
                try:
                    from allauth.socialaccount.models import SocialApp, SocialAppSite
                    from django.contrib.sites.models import Site
                    
                    logger.warning("Attempting automatic cleanup of duplicate SocialApps...")
                    
                    current_site = Site.objects.get_current()
                    google_apps = SocialApp.objects.filter(provider='google').order_by('-id')
                    
                    if google_apps.count() > 1:
                        keep_app = google_apps[0]
                        for app in google_apps[1:]:
                            SocialAppSite.objects.filter(app=app).delete()
                            app.delete()
                            logger.info(f"Deleted duplicate SocialApp {app.id}")
                        
                        # Link kept app to site
                        SocialAppSite.objects.get_or_create(
                            app=keep_app,
                            site=current_site
                        )
                        logger.info("Cleanup completed. Redirecting to retry...")
                        
                        # Redirect back to the same URL to retry
                        return HttpResponseRedirect(request.get_full_path())
                except Exception as cleanup_error:
                    logger.error(f"Cleanup attempt failed: {cleanup_error}", exc_info=True)
                    
                # Return a friendly error response
                if request.path.startswith('/accounts/'):
                    return JsonResponse(
                        {
                            'error': 'OAuth configuration error',
                            'message': 'We are resolving an OAuth configuration issue. Please try again in a moment.',
                            'retry_after': 5
                        },
                        status=503
                    )
            
            # Re-raise if not a MultipleObjectsReturned error
            raise
