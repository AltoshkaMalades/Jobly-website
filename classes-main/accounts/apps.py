import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        """
        This method is called when Django starts up.
        We use it to:
        1. Import the adapters module to trigger the monkey patch for allauth
        2. Register signal handlers for post_migrate cleanup
        3. Perform immediate cleanup of duplicate SocialApp entries
        """
        # Import the adapters module to trigger the monkey patch
        try:
            from . import adapters  # noqa: F401
        except Exception as e:
            logger.warning(f"Failed to import adapters module: {e}")
        
        # Register signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception as e:
            logger.warning(f"Failed to import signals module: {e}")
        
        # Perform immediate cleanup on startup
        self._cleanup_socialapps_on_startup()
    
    def _cleanup_socialapps_on_startup(self):
        """Cleanup duplicate SocialApp entries on app startup."""
        try:
            from allauth.socialaccount.models import SocialApp, SocialAppSite
            from django.contrib.sites.models import Site
        except ImportError:
            logger.debug("allauth not installed, skipping SocialApp cleanup on startup")
            return
        
        try:
            # Get current site
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            logger.debug("No Site object found, skipping SocialApp cleanup on startup")
            return
        except Exception as e:
            logger.debug(f"Error getting current site: {e}")
            return
        
        try:
            # Check for duplicate Google apps
            google_apps = SocialApp.objects.filter(provider='google').order_by('-id')
            count = google_apps.count()
            
            if count > 1:
                logger.warning(f"🔴 STARTUP: Found {count} Google SocialApp entries! Removing duplicates...")
                keep_app = google_apps[0]
                delete_apps = list(google_apps[1:])
                
                for app in delete_apps:
                    try:
                        # Remove from all sites
                        SocialAppSite.objects.filter(app=app).delete()
                        # Delete the app
                        app_id = app.id
                        app.delete()
                        logger.info(f"🧹 STARTUP: Deleted duplicate Google SocialApp (ID: {app_id})")
                    except Exception as e:
                        logger.error(f"Error deleting SocialApp on startup: {e}")
                
                # Ensure kept app is linked to current site
                try:
                    SocialAppSite.objects.get_or_create(
                        app=keep_app,
                        site=current_site
                    )
                    logger.info(f"✅ STARTUP: Google SocialApp {keep_app.id} is linked to site {current_site}")
                except Exception as e:
                    logger.error(f"Error linking SocialApp to site on startup: {e}")
            elif count == 1:
                logger.info(f"✅ STARTUP: 1 Google SocialApp found - OK")
            else:
                logger.debug("⚠️  STARTUP: No Google SocialApp found (will be created later)")
        except Exception as e:
            logger.warning(f"Error in _cleanup_socialapps_on_startup: {e}", exc_info=True)
