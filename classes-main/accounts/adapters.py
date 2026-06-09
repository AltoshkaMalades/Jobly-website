"""
Custom allauth adapters with MultipleObjectsReturned handling.
"""
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter that handles MultipleObjectsReturned gracefully.
    Fallback to the first (most recent) app if multiple exist.
    """

    def get_app(self, request, provider):
        """
        Override get_app to handle MultipleObjectsReturned.
        If multiple apps exist for a provider, use the first (most recent) one.
        """
        try:
            return super().get_app(request, provider)
        except SocialApp.MultipleObjectsReturned:
            logger.warning(f"Multiple SocialApp entries found for {provider}. Using fallback logic.")
            try:
                # Get the current site
                if request:
                    current_site = Site.objects.get_current()
                else:
                    current_site = Site.objects.get_default()
                
                # Get the first app for this provider that's linked to current site
                app = (
                    SocialApp.objects
                    .filter(provider=provider, sites=current_site)
                    .order_by('-id')
                    .first()
                )
                
                if not app:
                    # If not linked to current site, get any app for this provider
                    app = (
                        SocialApp.objects
                        .filter(provider=provider)
                        .order_by('-id')
                        .first()
                    )
                
                if app:
                    logger.info(f"Using SocialApp {app.id} for provider {provider}")
                    return app
                else:
                    logger.error(f"No {provider} app found even after MultipleObjectsReturned")
                    raise SocialApp.DoesNotExist(f"No {provider} app found")
            except Exception as e:
                logger.error(f"Error in CustomSocialAccountAdapter.get_app: {str(e)}", exc_info=True)
                raise


# Monkey patch DefaultSocialAccountAdapter.get_app to handle MultipleObjectsReturned
# This is a backup approach in case SOCIALACCOUNT_ADAPTER setting doesn't work
_original_get_app = DefaultSocialAccountAdapter.get_app


def _patched_get_app(self, request, provider):
    """
    Patched version of get_app that handles MultipleObjectsReturned.
    """
    try:
        return _original_get_app(self, request, provider)
    except SocialApp.MultipleObjectsReturned:
        logger.warning(f"[PATCHED] Multiple SocialApp entries found for {provider}. Using fallback logic.")
        try:
            if request:
                current_site = Site.objects.get_current()
            else:
                current_site = Site.objects.get_default()
            
            app = (
                SocialApp.objects
                .filter(provider=provider, sites=current_site)
                .order_by('-id')
                .first()
            )
            
            if not app:
                app = (
                    SocialApp.objects
                    .filter(provider=provider)
                    .order_by('-id')
                    .first()
                )
            
            if app:
                logger.info(f"[PATCHED] Using SocialApp {app.id} for provider {provider}")
                return app
            else:
                logger.error(f"[PATCHED] No {provider} app found")
                raise SocialApp.DoesNotExist(f"No {provider} app found")
        except SocialApp.DoesNotExist:
            raise
        except Exception as e:
            logger.error(f"[PATCHED] Error in get_app fallback: {str(e)}", exc_info=True)
            raise


# Apply the monkey patch as a failsafe
DefaultSocialAccountAdapter.get_app = _patched_get_app
logger.info("Applied monkey patch to DefaultSocialAccountAdapter.get_app")

