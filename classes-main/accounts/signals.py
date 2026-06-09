"""
Signal handlers for accounts app.
Ensures SocialApp duplicates are removed and properly configured.
Handles user profile creation for OAuth signups.
"""
import logging
from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def cleanup_socialapps_after_migrate(sender, **kwargs):
    """
    After migrations complete, cleanup duplicate SocialApp entries.
    This is a failsafe to ensure duplicates are removed at startup.
    """
    try:
        from allauth.socialaccount.models import SocialApp, SocialAppSite
        from django.contrib.sites.models import Site
    except ImportError:
        logger.debug("allauth not installed, skipping SocialApp cleanup")
        return
    
    try:
        # Get current site
        current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        logger.warning("No Site object found, skipping SocialApp cleanup")
        return
    
    # Check for duplicate Google apps
    google_apps = SocialApp.objects.filter(provider='google').order_by('-id')
    count = google_apps.count()
    
    if count > 1:
        logger.warning(f"Found {count} Google SocialApp entries! Removing duplicates...")
        keep_app = google_apps[0]
        delete_apps = list(google_apps[1:])
        
        for app in delete_apps:
            try:
                # Remove from all sites
                SocialAppSite.objects.filter(app=app).delete()
                # Delete the app
                app_id = app.id
                app.delete()
                logger.info(f"Deleted duplicate Google SocialApp (ID: {app_id})")
            except Exception as e:
                logger.error(f"Error deleting SocialApp: {e}")
        
        # Ensure kept app is linked to current site
        try:
            SocialAppSite.objects.get_or_create(
                app=keep_app,
                site=current_site
            )
            logger.info(f"Ensured Google SocialApp {keep_app.id} is linked to site {current_site}")
        except Exception as e:
            logger.error(f"Error linking SocialApp to site: {e}")


# Handle OAuth user signup to ensure profile is created
def _setup_allauth_signals():
    """Setup allauth signal handlers for OAuth signup."""
    try:
        from allauth.socialaccount.signals import pre_social_login, social_account_added
        
        @receiver(pre_social_login)
        def pre_social_login_handler(sender, request, sociallogin, **kwargs):
            """Ensure profile exists before OAuth login completes."""
            try:
                if sociallogin.is_new or sociallogin.user.id is None:
                    logger.info(f"New OAuth user detected: {sociallogin.user.email}")
            except Exception as e:
                logger.debug(f"Error in pre_social_login handler: {e}")
        
        @receiver(social_account_added)
        def social_account_added_handler(sender, request, sociallogin, **kwargs):
            """Create profile when OAuth account is added."""
            try:
                from accounts.models import Profile
                user = sociallogin.user
                profile, created = Profile.objects.get_or_create(user=user)
                if created:
                    logger.info(f"Created profile for OAuth user: {user.id} ({user.email})")
                else:
                    logger.debug(f"Profile already exists for OAuth user: {user.id}")
            except Exception as e:
                logger.error(f"Error in social_account_added_handler: {e}", exc_info=True)
        
        logger.info("Setup allauth signal handlers for OAuth signup")
    except ImportError:
        logger.debug("allauth signals not available")
    except Exception as e:
        logger.warning(f"Error setting up allauth signals: {e}")


_setup_allauth_signals()

