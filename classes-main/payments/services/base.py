"""
Base payment client interface.
All payment providers should implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PaymentClientError(Exception):
    """Base exception for payment client errors."""
    pass


class PaymentClient(ABC):
    """Abstract base class for payment providers."""
    
    @abstractmethod
    def create_payment_request(
        self,
        order_id: str,
        amount: int,
        currency: str,
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a payment request.
        
        Args:
            order_id: Unique order identifier
            amount: Amount in minor units (cents/tiyn)
            currency: ISO 4217 currency code (e.g., 'KZT')
            return_url: URL to redirect after payment
            **kwargs: Provider-specific parameters
        
        Returns:
            {
                'payment_url': str,           # URL for user to complete payment
                'transaction_id': str,        # Provider transaction ID
                'status': str,                # 'pending', 'completed', 'failed'
            }
        
        Raises:
            PaymentClientError: If payment creation fails
        """
        pass
    
    @abstractmethod
    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Retrieve current transaction status from provider.
        
        Returns:
            {
                'transaction_id': str,
                'status': str,     # 'pending', 'completed', 'failed'
                'metadata': dict,  # Provider-specific data
            }
        
        Raises:
            PaymentClientError: If status check fails
        """
        pass
    
    @abstractmethod
    def refund_transaction(
        self,
        transaction_id: str,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Refund a transaction (full or partial).
        
        Args:
            transaction_id: Provider transaction ID
            amount: Amount to refund (if None, refund full amount)
        
        Returns:
            {
                'refund_id': str,
                'status': str,        # 'completed', 'failed'
                'amount': int,        # Amount refunded
                'metadata': dict,
            }
        
        Raises:
            PaymentClientError: If refund fails
        """
        pass
    
    @abstractmethod
    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Validate webhook signature from provider.
        
        Args:
            payload: Raw request body
            signature: Signature header from provider
        
        Returns:
            True if signature is valid, False otherwise
        """
        pass
