"""
Retry utilities with exponential backoff for payment operations.
"""
import logging
import time
from functools import wraps
from typing import TypeVar, Callable, Any
from random import uniform

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Callable[[F], F]:
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between attempts
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to prevent thundering herd
    
    Usage:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        def call_payment_api():
            return requests.post(...)
    """
    
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"[RETRY] Attempt {attempt}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"[RETRY] Failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )
                    
                    # Add jitter if enabled
                    if jitter:
                        delay += uniform(0, delay * 0.1)
                    
                    logger.warning(
                        f"[RETRY] Attempt {attempt} failed: {str(e)} | "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            # Should not reach here
            raise last_exception
        
        return wrapper
    
    return decorator


class RetryConfig:
    """Configuration for retry behavior."""
    
    # Payment API calls
    PAYMENT_API_ATTEMPTS = 3
    PAYMENT_API_BASE_DELAY = 1.0
    PAYMENT_API_MAX_DELAY = 30.0
    
    # Webhook delivery
    WEBHOOK_ATTEMPTS = 5
    WEBHOOK_BASE_DELAY = 2.0
    WEBHOOK_MAX_DELAY = 60.0
    
    # Status checks
    STATUS_CHECK_ATTEMPTS = 3
    STATUS_CHECK_BASE_DELAY = 0.5
    STATUS_CHECK_MAX_DELAY = 10.0
