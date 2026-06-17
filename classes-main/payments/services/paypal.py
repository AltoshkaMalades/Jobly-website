"""
PayPal Sandbox payment provider client.
Uses PayPal Orders API v2.
"""
import os
import logging
import uuid
import base64
from typing import Dict, Any, Optional
from datetime import datetime
import requests
import hmac
import hashlib

from .base import PaymentClient, PaymentClientError
from .retry import retry_with_backoff, RetryConfig

logger = logging.getLogger(__name__)


class PayPalClient(PaymentClient):
    """
    PayPal Sandbox integration using Orders API v2.
    
    Environment variables:
        PAYPAL_CLIENT_ID: PayPal client ID
        PAYPAL_CLIENT_SECRET: PayPal client secret
        PAYPAL_SANDBOX: true/false (default: true for development)
        PAYPAL_WEBHOOK_ID: Webhook ID for signature validation (optional)
    """
    
    def __init__(self):
        self.sandbox = os.environ.get('PAYPAL_SANDBOX', 'true').lower() == 'true'
        self.api_url = (
            'https://api-m.sandbox.paypal.com' if self.sandbox
            else 'https://api-m.paypal.com'
        )
        self.client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
        self.client_secret = os.environ.get('PAYPAL_CLIENT_SECRET', '')
        self.webhook_id = os.environ.get('PAYPAL_WEBHOOK_ID', '')
        
        self.session = requests.Session()
        self.session.timeout = 10
        self._access_token = None
        self._token_expiry = None
        
        if not self.client_id or not self.client_secret:
            logger.warning('PayPal credentials not configured - using mock mode')
    
    def create_payment_request(
        self,
        order_id: str,
        amount: int,
        currency: str,
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create payment order with PayPal."""
        
        try:
            transaction_id = f"PAYPAL-{uuid.uuid4().hex[:12].upper()}"
            
            # Convert minor units to major units (cents to dollars, tiyn to tenge)
            amount_major = amount / 100
            
            if not self.client_id or not self.client_secret:
                logger.info(f"[PAYPAL] Mock payment request | Order: {order_id} | Amount: {amount_major} {currency}")
                return {
                    'payment_url': f'https://sandbox.paypal.com/checkoutnow?token={transaction_id}',
                    'transaction_id': transaction_id,
                    'status': 'pending',
                    'metadata': {
                        'order_id': order_id,
                        'amount': amount,
                        'currency': currency,
                        'provider': 'paypal',
                        'created_at': datetime.utcnow().isoformat(),
                    }
                }
            
            # Real API call
            payload = {
                'intent': 'CAPTURE',
                'purchase_units': [
                    {
                        'reference_id': order_id,
                        'amount': {
                            'currency_code': currency,
                            'value': f'{amount_major:.2f}',
                        },
                        'description': kwargs.get('description', 'Order'),
                    }
                ],
                'application_context': {
                    'return_url': return_url,
                    'cancel_url': return_url,
                    'locale': 'en-US',
                    'brand_name': 'Payment',
                },
            }
            
            headers = self._get_auth_headers()
            
            response = self.session.post(
                f'{self.api_url}/v2/checkout/orders',
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Get approval link
            approval_url = next(
                (link['href'] for link in data.get('links', []) if link['rel'] == 'approve'),
                ''
            )
            
            logger.info(f"[PAYPAL] Payment created | Order: {order_id} | PayPal Order: {data.get('id')}")
            
            return {
                'payment_url': approval_url,
                'transaction_id': data.get('id', transaction_id),
                'status': 'pending',
                'metadata': {
                    'paypal_order_id': data.get('id'),
                    'status': data.get('status', 'CREATED'),
                },
            }
        
        except requests.RequestException as e:
            error_msg = f"PayPal API error: {str(e)}"
            logger.error(error_msg)
            raise PaymentClientError(error_msg) from e
    
    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check PayPal order status."""
        
        try:
            if not self.client_id or not self.client_secret:
                logger.info(f"[PAYPAL] Mock status check | Transaction: {transaction_id}")
                return {
                    'transaction_id': transaction_id,
                    'status': 'pending',
                    'metadata': {'provider': 'paypal'},
                }
            
            headers = self._get_auth_headers()
            
            response = self.session.get(
                f'{self.api_url}/v2/checkout/orders/{transaction_id}',
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'transaction_id': transaction_id,
                'status': self._normalize_status(data.get('status', 'UNKNOWN')),
                'metadata': {
                    'paypal_status': data.get('status'),
                    'purchase_units': data.get('purchase_units', []),
                },
            }
        
        except requests.RequestException as e:
            error_msg = f"PayPal status check failed: {str(e)}"
            logger.error(error_msg)
            raise PaymentClientError(error_msg) from e
    
    def refund_transaction(
        self,
        transaction_id: str,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """Refund a PayPal capture."""
        
        try:
            refund_id = f"REFUND-{uuid.uuid4().hex[:12].upper()}"
            
            if not self.client_id or not self.client_secret:
                logger.info(f"[PAYPAL] Mock refund | Transaction: {transaction_id} | Amount: {amount}")
                return {
                    'refund_id': refund_id,
                    'status': 'completed',
                    'amount': amount or 0,
                    'metadata': {'provider': 'paypal'},
                }
            
            # First, get the order to find the capture ID
            order_data = self._get_order_details(transaction_id)
            capture_id = None
            
            for pu in order_data.get('purchase_units', []):
                for payment in pu.get('payments', {}).get('captures', []):
                    capture_id = payment.get('id')
                    break
            
            if not capture_id:
                raise PaymentClientError("No capture found for refund")
            
            # Prepare refund payload
            refund_payload = {}
            if amount:
                # Partial refund
                refund_payload['amount'] = {
                    'currency_code': order_data.get('purchase_units', [{}])[0].get('amount', {}).get('currency_code', 'USD'),
                    'value': f'{amount / 100:.2f}',
                }
            
            headers = self._get_auth_headers()
            
            response = self.session.post(
                f'{self.api_url}/v2/payments/captures/{capture_id}/refund',
                json=refund_payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"[PAYPAL] Refund initiated | Capture: {capture_id} | Refund: {data.get('id')}")
            
            return {
                'refund_id': data.get('id', refund_id),
                'status': 'completed',
                'amount': amount or 0,
                'metadata': {
                    'paypal_refund_id': data.get('id'),
                    'status': data.get('status', 'COMPLETED'),
                },
            }
        
        except Exception as e:
            error_msg = f"PayPal refund failed: {str(e)}"
            logger.error(error_msg)
            raise PaymentClientError(error_msg) from e
    
    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate PayPal webhook signature."""
        
        if not self.webhook_id:
            logger.warning("PAYPAL_WEBHOOK_ID not configured - skipping signature validation")
            return True
        
        if not self.client_id or not self.client_secret:
            logger.warning("PayPal credentials not configured - accepting webhook")
            return True
        
        try:
            headers = self._get_auth_headers()
            
            # Verify signature using PayPal API
            verify_payload = {
                'webhook_id': self.webhook_id,
                'event_body': payload.decode('utf-8'),
                'transmission_id': signature,  # Simplified for now
                'transmission_time': '',
                'cert_url': '',
            }
            
            response = self.session.post(
                f'{self.api_url}/v1/notifications/verify-webhook-signature',
                json=verify_payload,
                headers=headers
            )
            
            data = response.json()
            return data.get('verification_status') == 'SUCCESS'
        
        except Exception as e:
            logger.error(f"PayPal webhook validation error: {str(e)}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for PayPal API."""
        
        auth_str = base64.b64encode(
            f'{self.client_id}:{self.client_secret}'.encode()
        ).decode()
        
        return {
            'Authorization': f'Basic {auth_str}',
            'Content-Type': 'application/json',
        }
    
    def _get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get PayPal order details."""
        
        headers = self._get_auth_headers()
        
        response = self.session.get(
            f'{self.api_url}/v2/checkout/orders/{order_id}',
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
    
    @staticmethod
    def _normalize_status(paypal_status: str) -> str:
        """Normalize PayPal status to standard status."""
        
        status_map = {
            'CREATED': 'pending',
            'SAVED': 'pending',
            'APPROVED': 'pending',
            'VOIDED': 'failed',
            'COMPLETED': 'completed',
            'PAYER_ACTION_REQUIRED': 'pending',
        }
        
        return status_map.get(paypal_status.upper(), 'pending')
