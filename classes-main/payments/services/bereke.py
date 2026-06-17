"""
Bereke Bank Sandbox payment provider client.
"""
import os
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import hmac
import hashlib

from .base import PaymentClient, PaymentClientError
from .retry import retry_with_backoff, RetryConfig

logger = logging.getLogger(__name__)


class BereкeBankClient(PaymentClient):
    """
    Bereke Bank Sandbox integration.
    
    Environment variables:
        BEREKE_API_KEY: API key for Bereke Bank
        BEREKE_API_SECRET: API secret for webhook validation
        BEREKE_MERCHANT_ID: Merchant ID
        BEREKE_SANDBOX: true/false (default: true for development)
        BEREKE_API_URL: Sandbox API URL (optional)
    """
    
    def __init__(self):
        self.sandbox = os.environ.get('BEREKE_SANDBOX', 'true').lower() == 'true'
        self.api_url = os.environ.get(
            'BEREKE_API_URL',
            'https://api.berekebank-sandbox.kz' if self.sandbox else 'https://api.berekebank.kz'
        )
        self.api_key = os.environ.get('BEREKE_API_KEY', '')
        self.api_secret = os.environ.get('BEREKE_API_SECRET', '')
        self.merchant_id = os.environ.get('BEREKE_MERCHANT_ID', 'MERCHANT_001')
        
        self.session = requests.Session()
        self.session.timeout = 10
        
        if not self.api_key:
            logger.warning('BEREKE_API_KEY not configured - using mock mode')
    
    def create_payment_request(
        self,
        order_id: str,
        amount: int,
        currency: str,
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create payment request with Bereke Bank."""
        
        try:
            transaction_id = f"BEREKE-{uuid.uuid4().hex[:12].upper()}"
            
            # In sandbox without credentials, return mock response
            if not self.api_key:
                logger.info(f"[BEREKE] Mock payment request | Order: {order_id} | Amount: {amount} {currency}")
                return {
                    'payment_url': f'https://sandbox.berekebank.kz/pay/{transaction_id}',
                    'transaction_id': transaction_id,
                    'status': 'pending',
                    'metadata': {
                        'order_id': order_id,
                        'amount': amount,
                        'currency': currency,
                        'provider': 'bereke',
                        'created_at': datetime.utcnow().isoformat(),
                    }
                }
            
            # Real API call (when credentials are available) with retry
            return self._create_payment_request_with_retry(
                order_id, amount, currency, return_url, **kwargs
            )
        
        except Exception as e:
            error_msg = f"Bereke payment creation failed: {str(e)}"
            logger.error(error_msg)
            raise PaymentClientError(error_msg) from e
    
    @retry_with_backoff(
        max_attempts=RetryConfig.PAYMENT_API_ATTEMPTS,
        base_delay=RetryConfig.PAYMENT_API_BASE_DELAY,
        max_delay=RetryConfig.PAYMENT_API_MAX_DELAY
    )
    def _create_payment_request_with_retry(
        self,
        order_id: str,
        amount: int,
        currency: str,
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Internal method with retry logic for API call."""
        
        transaction_id = f"BEREKE-{uuid.uuid4().hex[:12].upper()}"
        
        payload = {
            'merchantId': self.merchant_id,
            'orderId': order_id,
            'amount': amount,
            'currency': currency,
            'returnUrl': return_url,
            'description': kwargs.get('description', ''),
            'transactionId': transaction_id,
        }
        
        headers = self._get_auth_headers(payload)
        
        response = self.session.post(
            f'{self.api_url}/v1/payment/create',
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        data = response.json()
        
        logger.info(f"[BEREKE] Payment created | Order: {order_id} | Transaction: {transaction_id}")
        
        return {
            'payment_url': data.get('paymentUrl', ''),
            'transaction_id': transaction_id,
            'status': 'pending',
            'metadata': data.get('metadata', {}),
        }
    
    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check transaction status from Bereke Bank."""
        
        try:
            if not self.api_key:
                # Mock response
                logger.info(f"[BEREKE] Mock status check | Transaction: {transaction_id}")
                return {
                    'transaction_id': transaction_id,
                    'status': 'pending',
                    'metadata': {'provider': 'bereke'},
                }
            
            payload = {
                'transactionId': transaction_id,
                'merchantId': self.merchant_id,
            }
            
            headers = self._get_auth_headers(payload)
            
            response = self.session.post(
                f'{self.api_url}/v1/payment/status',
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'transaction_id': transaction_id,
                'status': self._normalize_status(data.get('status', 'unknown')),
                'metadata': data.get('metadata', {}),
            }
        
        except requests.RequestException as e:
            error_msg = f"Bereke status check failed: {str(e)}"
            logger.error(error_msg)
            raise PaymentClientError(error_msg) from e
    
    def refund_transaction(
        self,
        transaction_id: str,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """Refund a Bereke Bank transaction."""
        
        try:
            refund_id = f"REFUND-{uuid.uuid4().hex[:12].upper()}"
            
            if not self.api_key:
                logger.info(f"[BEREKE] Mock refund | Transaction: {transaction_id} | Amount: {amount}")
                return {
                    'refund_id': refund_id,
                    'status': 'completed',
                    'amount': amount or 0,
                    'metadata': {'provider': 'bereke'},
                }
            
            payload = {
                'transactionId': transaction_id,
                'merchantId': self.merchant_id,
                'refundId': refund_id,
                'amount': amount,
            }
            
            headers = self._get_auth_headers(payload)
            
            response = self.session.post(
                f'{self.api_url}/v1/payment/refund',
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"[BEREKE] Refund initiated | Transaction: {transaction_id} | Refund: {refund_id}")
            
            return {
                'refund_id': refund_id,
                'status': self._normalize_status(data.get('status', 'unknown')),
                'amount': amount or 0,
                'metadata': data.get('metadata', {}),
            }
        
        except requests.RequestException as e:
            error_msg = f"Bereke refund failed: {str(e)}"
            logger.error(error_msg)
            raise PaymentClientError(error_msg) from e
    
    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate Bereke Bank webhook signature using HMAC-SHA256."""
        
        if not self.api_secret:
            logger.warning("BEREKE_API_SECRET not configured - skipping signature validation")
            return True
        
        try:
            expected_signature = hmac.new(
                self.api_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        
        except Exception as e:
            logger.error(f"Webhook signature validation error: {str(e)}")
            return False
    
    def _get_auth_headers(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Generate authentication headers for Bereke API."""
        
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Merchant-Id': self.merchant_id,
        }
    
    @staticmethod
    def _normalize_status(bereke_status: str) -> str:
        """Normalize Bereke status to standard status."""
        
        status_map = {
            'PAID': 'completed',
            'FAILED': 'failed',
            'PENDING': 'pending',
            'REFUNDED': 'refunded',
        }
        
        return status_map.get(bereke_status.upper(), 'pending')
