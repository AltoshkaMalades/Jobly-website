"""
Google Analytics 4 integration.
Tracks events for conversion funnels, user actions, and analytics dashboards.
"""
import os
import logging

logger = logging.getLogger(__name__)


def get_ga4_measurement_id() -> str:
    """Get GA4 Measurement ID from environment."""
    return os.environ.get('GA4_MEASUREMENT_ID', '')


def get_ga4_api_secret() -> str:
    """Get GA4 API Secret from environment."""
    return os.environ.get('GA4_API_SECRET', '')


def is_ga4_enabled() -> bool:
    """Check if GA4 is configured."""
    return bool(get_ga4_measurement_id())


class GA4EventTracker:
    """Helper class for tracking GA4 events via Measurement Protocol."""
    
    def __init__(self):
        self.measurement_id = get_ga4_measurement_id()
        self.api_secret = get_ga4_api_secret()
        self.enabled = is_ga4_enabled()
    
    def track_event(self, event_name: str, user_id: str = None, properties: dict = None):
        """
        Queue GA4 event for tracking.
        
        In production, events are sent via the Measurement Protocol API.
        For now, this tracks events client-side via the gtag() function.
        
        Args:
            event_name: Name of the event (e.g., 'sign_up', 'purchase', 'checkout_started')
            user_id: Optional user ID for user-level tracking
            properties: Optional dict of event properties/parameters
        """
        if not self.enabled:
            return
        
        if properties is None:
            properties = {}
        
        # Client-side event tracking is handled via gtag() in the template
        # Server-side event logging can be added here for audit trails
        logger.debug(f"GA4 Event: {event_name} with properties: {properties}")


# Global instance
_ga4_tracker = None


def get_ga4_tracker() -> GA4EventTracker:
    """Get or create GA4 tracker instance."""
    global _ga4_tracker
    if _ga4_tracker is None:
        _ga4_tracker = GA4EventTracker()
    return _ga4_tracker
