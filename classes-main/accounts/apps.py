from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        """
        This method is called when Django starts up.
        We use it to:
        1. Import the adapters module to trigger the monkey patch for allauth
        2. Register signal handlers for post_migrate cleanup
        """
        # Import the adapters module to trigger the monkey patch
        try:
            from . import adapters  # noqa: F401
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to import adapters module: {e}")
        
        # Register signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to import signals module: {e}")
