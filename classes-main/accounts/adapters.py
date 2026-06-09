"""
Custom allauth adapters with MultipleObjectsReturned handling.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


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
            # Multiple apps found - use the first one (most recent by ID)
            try:
                # Get the current site
                if request:
                    current_site = Site.objects.get_current()
                else:
                    current_site = Site.objects.get_default()
                
                # Get the first app for this provider
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
                    return app
                else:
                    raise SocialApp.DoesNotExist(f"No {provider} app found")
            except Exception as e:
                # Log the error and re-raise the original exception
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in CustomSocialAccountAdapter.get_app: {str(e)}")
                raise
