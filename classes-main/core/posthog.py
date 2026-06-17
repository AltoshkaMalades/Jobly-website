"""
PostHog analytics integration.
Tracks events for analytics, funnels, and dashboards.
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from posthog import Posthog
    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False
    logger.warning("PostHog not installed - analytics will be disabled")


# Initialize PostHog client (singleton)
_posthog_client = None


def get_posthog_client():
    """Get or create PostHog client."""
    global _posthog_client
    
    if not POSTHOG_AVAILABLE:
        return None
    
    if _posthog_client is None:
        api_key = os.environ.get('POSTHOG_API_KEY')
        api_url = os.environ.get('POSTHOG_API_URL', 'https://app.posthog.com')
        
        if api_key:
            _posthog_client = Posthog(
                api_key=api_key,
                host=api_url,
                debug=os.environ.get('DEBUG', 'False').lower() == 'true',
            )
            logger.info("PostHog client initialized")
        else:
            logger.warning("POSTHOG_API_KEY not configured - analytics disabled")
    
    return _posthog_client


def identify_user(user_id: str, user_properties: Optional[Dict[str, Any]] = None):
    """
    Identify user in PostHog.
    
    Args:
        user_id: Unique user identifier
        user_properties: Dictionary of user properties (name, email, plan, etc.)
    """
    
    client = get_posthog_client()
    if not client:
        return
    
    try:
        properties = user_properties or {}
        client.identify(
            distinct_id=str(user_id),
            properties=properties
        )
        logger.debug(f"User identified in PostHog: {user_id}")
    
    except Exception as e:
        logger.error(f"PostHog identify failed: {str(e)}")


def track_event(event_name: str, properties: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None):
    """
    Track an event in PostHog.
    
    Args:
        event_name: Event name (e.g., 'checkout_started', 'payment_completed')
        properties: Event properties
        user_id: User ID (for anonymous tracking if not identified)
    """
    
    client = get_posthog_client()
    if not client:
        return
    
    try:
        distinct_id = user_id or 'anonymous'
        properties = properties or {}
        
        client.capture(
            distinct_id=str(distinct_id),
            event=event_name,
            properties=properties
        )
        logger.debug(f"Event tracked: {event_name} | User: {distinct_id}")
    
    except Exception as e:
        logger.error(f"PostHog track event failed: {str(e)}")


def set_user_properties(user_id: str, properties: Dict[str, Any]):
    """
    Update user properties in PostHog.
    
    Args:
        user_id: User ID
        properties: Properties to set
    """
    
    client = get_posthog_client()
    if not client:
        return
    
    try:
        client.identify(
            distinct_id=str(user_id),
            properties=properties
        )
        logger.debug(f"User properties updated: {user_id}")
    
    except Exception as e:
        logger.error(f"PostHog set properties failed: {str(e)}")


# Business event schemas
EVENTS = {
    # Acquisition
    'signup': 'User signs up',
    
    # Activation
    'onboarding_complete': 'User completes onboarding',
    
    # Revenue
    'checkout_started': 'User initiates checkout',
    'payment_completed': 'Payment successful',
    'payment_failed': 'Payment failed',
    'payment_duplicated': 'Duplicate payment detected (idempotent)',
    'refund_initiated': 'Refund initiated',
}
