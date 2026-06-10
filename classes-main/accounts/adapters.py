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
        except Exception as e:
            # Catch MultipleObjectsReturned by checking class name, not type
            # This handles Django's model-specific exception classes
            if e.__class__.__name__ == 'MultipleObjectsReturned':
                logger.warning(f"[CustomAdapter] Multiple SocialApp entries found for {provider}. Using fallback logic.")
                try:
                    # Get the current site
                    if request:
                        current_site = Site.objects.get_current()
                    else:
                        # For None request, use first site or get_current()
                        current_site = Site.objects.get_current()
                    
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
                        logger.info(f"[CustomAdapter] Using SocialApp {app.id} for provider {provider}")
                        return app
                    else:
                        logger.error(f"[CustomAdapter] No {provider} app found even after MultipleObjectsReturned")
                        raise
                except Exception as inner_e:
                    if inner_e.__class__.__name__ != 'MultipleObjectsReturned':
                        logger.error(f"[CustomAdapter] Error in fallback: {str(inner_e)}", exc_info=True)
                    raise e  # Re-raise the original exception
            else:
                # Not a MultipleObjectsReturned error, re-raise
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
    except Exception as e:
        # Catch MultipleObjectsReturned by checking exception class name
        # because Django creates model-specific exception classes
        if e.__class__.__name__ == 'MultipleObjectsReturned':
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
                    raise
            except Exception as inner_e:
                if inner_e.__class__.__name__ != 'MultipleObjectsReturned':
                    logger.error(f"[PATCHED] Error in fallback: {str(inner_e)}", exc_info=True)
                raise e  # Re-raise the original exception
        else:
            # Not a MultipleObjectsReturned error, re-raise
            raise



# Apply the monkey patch as a failsafe
DefaultSocialAccountAdapter.get_app = _patched_get_app
logger.info("Applied monkey patch to DefaultSocialAccountAdapter.get_app")


# Monkey patch OAuth2View and OAuth2CallbackView to handle MultipleObjectsReturned
def _patch_oauth2_views():
    """Patch allauth OAuth2 views to handle MultipleObjectsReturned."""
    try:
        from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
        from .oauth_views import PatchedOAuth2View, PatchedOAuth2CallbackView
        
        # Store original views
        _original_OAuth2View = OAuth2Adapter
        
        # Patch the dispatch method directly on OAuth2Adapter
        _original_oauth2_dispatch = OAuth2Adapter.dispatch
        
        def _patched_oauth2_dispatch(self, request, *args, **kwargs):
            """Patched dispatch that handles MultipleObjectsReturned."""
            try:
                return _original_oauth2_dispatch(self, request, *args, **kwargs)
            except SocialApp.MultipleObjectsReturned:
                logger.warning(f"MultipleObjectsReturned caught in OAuth2Adapter")
                
                # Get provider from the request
                provider = getattr(self, 'provider', None)
                if provider:
                    try:
                        apps = SocialApp.objects.filter(
                            provider=provider.id
                        ).order_by('-id')
                        
                        if apps.exists():
                            app = apps.first()
                            logger.info(f"Using SocialApp {app.id} as fallback")
                            
                            # Retry with our choice
                            original_get_app = self.adapter.get_app
                            self.adapter.get_app = lambda request, prov: app
                            result = _original_oauth2_dispatch(self, request, *args, **kwargs)
                            self.adapter.get_app = original_get_app
                            return result
                    except Exception as e:
                        logger.error(f"Fallback failed: {e}", exc_info=True)
                
                raise
        
        OAuth2Adapter.dispatch = _patched_oauth2_dispatch
        logger.info("Applied patch to OAuth2Adapter.dispatch")
    except ImportError:
        logger.debug("Could not import OAuth2 views for patching")
    except Exception as e:
        logger.warning(f"Error patching OAuth2 views: {e}")


# Create a custom manager that handles MultipleObjectsReturned
def _create_custom_manager():
    """Create a custom manager for SocialApp that handles MultipleObjectsReturned."""
    try:
        from allauth.socialaccount.models import SocialApp, SocialAppManager
        from django.db.models import Manager
        
        class SafeSocialAppManager(SocialAppManager):
            """Custom manager that handles MultipleObjectsReturned gracefully."""
            
            def get(self, *args, **kwargs):
                """Override get to handle MultipleObjectsReturned."""
                try:
                    return super().get(*args, **kwargs)
                except SocialApp.MultipleObjectsReturned:
                    logger.warning(f"MultipleObjectsReturned in SafeSocialAppManager.get({kwargs}). Using fallback.")
                    
                    # Use filter + first() to get the most recent one
                    results = self.filter(*args, **kwargs).order_by('-id')
                    if results.exists():
                        app = results.first()
                        logger.info(f"[SafeSocialAppManager] Using app {app.id}")
                        return app
                    
                    # If no results found after filtering, raise DoesNotExist
                    raise SocialApp.DoesNotExist(f"SocialApp matching query does not exist.")
        
        # Replace the default manager
        SocialApp.objects = SafeSocialAppManager()
        SocialApp.objects.model = SocialApp
        logger.info("Replaced SocialApp.objects with SafeSocialAppManager")
    except Exception as e:
        logger.warning(f"Could not replace SocialApp manager: {e}", exc_info=True)


_create_custom_manager()


# CRITICAL: Patch QuerySet.get() to handle MultipleObjectsReturned for SocialApp
# This is the most fundamental fix - it applies at the ORM level for all .get() calls
def _patch_queryset_get():
    """
    Patch Django's QuerySet.get() to handle MultipleObjectsReturned gracefully.
    This is the deepest level of patching - applies to ALL database queries.
    """
    try:
        from django.db.models.query import QuerySet
        from django.core.exceptions import MultipleObjectsReturned as DjangoMultipleObjectsReturned
        
        # Store the original get method
        _original_queryset_get = QuerySet.get
        
        def _safe_queryset_get(self, *args, **kwargs):
            """Patched QuerySet.get that handles MultipleObjectsReturned for SocialApp."""
            try:
                return _original_queryset_get(self, *args, **kwargs)
            except Exception as e:
                # Check if this is MultipleObjectsReturned and if it's for SocialApp
                if (hasattr(e, '__class__') and 
                    e.__class__.__name__ == 'MultipleObjectsReturned' and 
                    self.model.__name__ == 'SocialApp'):
                    logger.warning(f"[ORM Patch] MultipleObjectsReturned caught in SocialApp.get({kwargs})")
                    
                    # Use filter + order_by + first to get the most recent one
                    try:
                        qs = self.filter(**kwargs).order_by('-id')
                        if qs.exists():
                            obj = qs.first()
                            logger.info(f"[ORM Patch] Using SocialApp ID {obj.id} as fallback")
                            return obj
                        else:
                            logger.error(f"[ORM Patch] No SocialApp found after filter, re-raising exception")
                            raise
                    except Exception as inner_e:
                        logger.error(f"[ORM Patch] Error in fallback logic: {inner_e}")
                        raise e  # Re-raise the original exception
                else:
                    # Don't patch other models, re-raise the exception
                    raise
        
        # Apply the patch
        QuerySet.get = _safe_queryset_get
        logger.info("[ORM Patch] Applied patch to QuerySet.get()")
    except Exception as e:
        logger.warning(f"Could not patch QuerySet.get: {e}", exc_info=True)


_patch_queryset_get()


