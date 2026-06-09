"""
Override allauth OAuth views to handle MultipleObjectsReturned errors.
"""
import logging
from allauth.socialaccount.providers.oauth2.views import OAuth2View, OAuth2CallbackView
from allauth.socialaccount.models import SocialApp

logger = logging.getLogger(__name__)


class PatchedOAuth2View(OAuth2View):
    """
    Patched OAuth2View that handles MultipleObjectsReturned from get_app()
    by using the first (most recent) app if multiple exist.
    """

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to catch MultipleObjectsReturned early."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except SocialApp.MultipleObjectsReturned:
            logger.warning(f"MultipleObjectsReturned in OAuth2View for provider {self.provider.id}")
            
            # Try to fix by using the first app
            try:
                apps = SocialApp.objects.filter(
                    provider=self.provider.id
                ).order_by('-id')
                
                if apps.exists():
                    app = apps.first()
                    logger.info(f"Using SocialApp {app.id} as fallback")
                    
                    # Create a temporary adapter that returns our chosen app
                    original_adapter = self.adapter
                    
                    class FallbackAdapter:
                        def get_app(self, request, provider):
                            return app
                        
                        def __getattr__(self, name):
                            # Delegate everything else to the original adapter
                            return getattr(original_adapter, name)
                    
                    self.adapter = FallbackAdapter()
                    return super().dispatch(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback failed: {e}", exc_info=True)
            
            raise


class PatchedOAuth2CallbackView(OAuth2CallbackView):
    """
    Patched OAuth2CallbackView that handles MultipleObjectsReturned from get_app()
    by using the first (most recent) app if multiple exist.
    """

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to catch MultipleObjectsReturned early."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except SocialApp.MultipleObjectsReturned:
            logger.warning(f"MultipleObjectsReturned in OAuth2CallbackView for provider {self.provider.id}")
            
            # Try to fix by using the first app
            try:
                apps = SocialApp.objects.filter(
                    provider=self.provider.id
                ).order_by('-id')
                
                if apps.exists():
                    app = apps.first()
                    logger.info(f"Using SocialApp {app.id} as fallback in callback")
                    
                    # Create a temporary adapter that returns our chosen app
                    original_adapter = self.adapter
                    
                    class FallbackAdapter:
                        def get_app(self, request, provider):
                            return app
                        
                        def __getattr__(self, name):
                            # Delegate everything else to the original adapter
                            return getattr(original_adapter, name)
                    
                    self.adapter = FallbackAdapter()
                    return super().dispatch(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback in callback failed: {e}", exc_info=True)
            
            raise
