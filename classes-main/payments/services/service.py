"""
Payment service orchestrator.
Handles payment processing, status checking, and provider abstraction.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import hashlib
import hmac

from payments.models import Order, Transaction
from payments.services.bereke import BereкeBankClient, PaymentClientError
from payments.services.paypal import PayPalClient
from core.posthog import track_event

logger = logging.getLogger(__name__)


# Provider factory
def get_payment_client(provider: str):
    """Get payment client for specified provider."""
    
    if provider == 'bereke':
        return BereкeBankClient()
    elif provider == 'paypal':
        return PayPalClient()
    else:
        raise ValueError(f"Unknown payment provider: {provider}")


class PaymentService:
    """Payment service for handling transactions."""
    
    DEFAULT_PROVIDER = 'bereke'
    
    @staticmethod
    def create_payment(
        user,
        order_id: str,
        amount: int,
        currency: str = 'KZT',
        description: str = '',
        provider: str = None,
        return_url: str = None,
    ) -> Dict[str, Any]:
        """
        Create a payment for an order.
        
        Args:
            user: Django User object
            order_id: Order ID (usually database ID)
            amount: Amount in minor units (cents/tiyn)
            currency: ISO 4217 currency code
            description: Order description
            provider: Payment provider (bereke, paypal)
            return_url: URL to redirect after payment
        
        Returns:
            {
                'success': bool,
                'order_id': str,
                'transaction_id': str,
                'payment_url': str,
                'error': str (if not successful),
            }
        """
        
        provider = provider or PaymentService.DEFAULT_PROVIDER
        
        try:
            # Create or get Order
            idempotency_key = PaymentService._generate_idempotency_key(
                user.id, order_id, amount
            )
            
            # Check for duplicate
            existing_transaction = Transaction.objects.filter(
                idempotency_key=idempotency_key
            ).first()
            
            if existing_transaction:
                logger.info(
                    f"[PAYMENT] Duplicate detected | User: {user.id} | "
                    f"Idempotency: {idempotency_key}"
                )
                track_event('payment_duplicated', {
                    'user_id': user.id,
                    'amount': amount,
                    'provider': provider,
                })
                return {
                    'success': True,  # Idempotent - return success
                    'order_id': order_id,
                    'transaction_id': existing_transaction.transaction_id,
                    'payment_url': existing_transaction.metadata.get('payment_url', ''),
                    'message': 'Payment already created'
                }
            
            # Create Order if doesn't exist
            order, created = Order.objects.get_or_create(
                idempotency_key=idempotency_key,
                defaults={
                    'user': user,
                    'amount': amount,
                    'currency': currency,
                    'description': description,
                    'status': 'created',
                }
            )
            
            if created:
                order.transition_to('pending', actor=f'user_{user.id}')
            
            # Initialize payment client
            client = get_payment_client(provider)
            
            # Create payment request
            payment_response = client.create_payment_request(
                order_id=str(order.id),
                amount=amount,
                currency=currency,
                return_url=return_url or '',
                description=description,
            )
            
            # Create Transaction record
            transaction = Transaction.objects.create(
                order=order,
                transaction_id=payment_response['transaction_id'],
                provider=provider,
                amount=amount,
                currency=currency,
                idempotency_key=idempotency_key,
                status='pending',
                metadata=payment_response.get('metadata', {}),
            )
            
            logger.info(
                f"[PAYMENT] Created | Order: {order.id} | User: {user.id} | "
                f"Provider: {provider} | Amount: {amount} {currency}"
            )
            
            # Track event
            track_event('checkout_started', {
                'user_id': user.id,
                'order_id': order.id,
                'amount': amount,
                'currency': currency,
                'provider': provider,
            })
            
            return {
                'success': True,
                'order_id': order.id,
                'transaction_id': transaction.transaction_id,
                'payment_url': payment_response['payment_url'],
            }
        
        except Exception as e:
            error_msg = f"Payment creation failed: {str(e)}"
            logger.error(error_msg)
            
            track_event('payment_failed', {
                'user_id': user.id,
                'amount': amount,
                'provider': provider,
                'error': str(e),
            })
            
            return {
                'success': False,
                'order_id': order_id,
                'error': error_msg,
            }
    
    @staticmethod
    def check_transaction_status(transaction_id: str) -> Dict[str, Any]:
        """Check and update transaction status from provider."""
        
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            
            # Get client for provider
            client = get_payment_client(transaction.provider)
            
            # Get status from provider
            status_response = client.get_transaction_status(transaction_id)
            
            # Update transaction if status changed
            old_status = transaction.status
            new_status = status_response.get('status', 'pending')
            
            if new_status != old_status:
                transaction.status = new_status
                transaction.metadata.update(status_response.get('metadata', {}))
                
                if new_status == 'completed':
                    transaction.completed_at = datetime.now(timezone.utc)
                    transaction.order.transition_to('paid', actor='webhook')
                elif new_status == 'failed':
                    transaction.order.transition_to('failed', actor='webhook')
                
                transaction.save()
                
                logger.info(
                    f"[PAYMENT] Status updated | Transaction: {transaction_id} | "
                    f"{old_status} → {new_status}"
                )
                
                # Track completion event
                if new_status == 'completed':
                    track_event('payment_completed', {
                        'user_id': transaction.order.user.id,
                        'order_id': transaction.order.id,
                        'transaction_id': transaction_id,
                        'amount': transaction.amount,
                        'provider': transaction.provider,
                    })
                elif new_status == 'failed':
                    track_event('payment_failed', {
                        'user_id': transaction.order.user.id,
                        'order_id': transaction.order.id,
                        'transaction_id': transaction_id,
                        'amount': transaction.amount,
                        'provider': transaction.provider,
                    })
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'status': transaction.status,
                'order_status': transaction.order.status,
            }
        
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found: {transaction_id}")
            return {
                'success': False,
                'error': 'Transaction not found',
            }
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }
    
    @staticmethod
    def refund_transaction(
        transaction_id: str,
        amount: Optional[int] = None,
        actor: str = 'system'
    ) -> Dict[str, Any]:
        """Refund a transaction."""
        
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            
            if transaction.status != 'completed':
                raise ValueError(f"Cannot refund transaction in {transaction.status} status")
            
            # Get client for provider
            client = get_payment_client(transaction.provider)
            
            # Request refund
            refund_response = client.refund_transaction(transaction_id, amount)
            
            # Update transaction
            if refund_response['status'] == 'completed':
                refund_amount = refund_response.get('amount', transaction.amount)
                transaction.refund_amount = refund_amount
                transaction.status = 'refunded'
                transaction.save()
                
                # Update order
                transaction.order.transition_to('refunded', actor=actor)
                
                logger.info(
                    f"[REFUND] Completed | Transaction: {transaction_id} | "
                    f"Amount: {refund_amount}"
                )
                
                # Track event
                track_event('refund_initiated', {
                    'user_id': transaction.order.user.id,
                    'order_id': transaction.order.id,
                    'transaction_id': transaction_id,
                    'refund_amount': refund_amount,
                    'provider': transaction.provider,
                })
                
                return {
                    'success': True,
                    'refund_id': refund_response.get('refund_id'),
                    'amount': refund_amount,
                }
            else:
                raise ValueError("Refund request failed on provider side")
        
        except Exception as e:
            error_msg = f"Refund failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
            }
    
    @staticmethod
    def _generate_idempotency_key(user_id: int, order_id: str, amount: int) -> str:
        """Generate deterministic idempotency key."""
        
        key_string = f"{user_id}:{order_id}:{amount}"
        return hashlib.sha256(key_string.encode()).hexdigest()
