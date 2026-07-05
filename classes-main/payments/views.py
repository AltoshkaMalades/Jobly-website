"""
Payment API endpoints.
"""
import logging
import json
import os
import uuid
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.conf import settings

from payments.models import Order, Transaction
from payments.services.service import PaymentService
from payments.services.bereke import BereкeBankClient
from payments.services.paypal import PayPalClient

logger = logging.getLogger(__name__)


@login_required
@login_required
@require_POST
def create_payment(request):
    """
    Create a new payment.
    
    POST /api/payments/create/
    
    Request body:
        {
            "amount": 10000,           # Amount in minor units (cents/tiyn)
            "currency": "KZT",         # ISO 4217 code
            "description": "Order #123",
            "provider": "bereke",      # or "paypal"
            "return_url": "https://..."
        }
    
    Response:
        {
            "success": bool,
            "order_id": int,
            "transaction_id": str,
            "payment_url": str,
            "error": str (if not successful)
        }
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    try:
        amount = int(data.get('amount', 0))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be positive'}, status=400)
        
        currency = data.get('currency', 'USD')
        description = data.get('description', '')
        provider = data.get('provider', 'paypal')
        return_url = data.get('return_url', request.build_absolute_uri('/'))
        is_subscription = bool(data.get('is_subscription', False)) or 'subscription' in description.lower()
        
        # Generate unique order ID
        unique_order_id = f"ORD-{request.user.id}-{uuid.uuid4().hex[:8].upper()}"
        
        result = PaymentService.create_payment(
            user=request.user,
            order_id=unique_order_id,
            amount=amount,
            currency=currency,
            description=description,
            provider=provider,
            return_url=return_url,
            is_subscription=is_subscription,
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
    
    except ValueError as e:
        logger.error(f"Payment creation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in create_payment: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_GET
def get_order_status(request, order_id):
    """
    Get order and transaction status.
    
    GET /api/payments/orders/<order_id>/
    
    Response:
        {
            "success": bool,
            "order": {
                "id": int,
                "status": str,
                "amount": int,
                "currency": str,
                "created_at": str
            },
            "transactions": [
                {
                    "transaction_id": str,
                    "provider": str,
                    "status": str,
                    "completed_at": str
                }
            ]
        }
    """
    
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        transactions = order.transactions.values(
            'transaction_id', 'provider', 'status', 'completed_at'
        )
        
        return JsonResponse({
            'success': True,
            'order': {
                'id': order.id,
                'status': order.status,
                'amount': order.amount,
                'currency': order.currency,
                'created_at': order.created_at.isoformat(),
            },
            'transactions': list(transactions),
        })
    
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")
        return JsonResponse({'error': 'Order not found'}, status=404)


@login_required
@require_GET
def get_transaction_status(request, transaction_id):
    """
    Get current transaction status from provider.
    
    GET /api/payments/transactions/<transaction_id>/
    
    Response:
        {
            "success": bool,
            "transaction_id": str,
            "status": str,
            "order_status": str,
            "error": str (if not successful)
        }
    """
    
    try:
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        
        # Verify user owns the order
        if transaction.order.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Check status from provider
        result = PaymentService.check_transaction_status(transaction_id)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
    
    except Exception as e:
        logger.error(f"Error getting transaction status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_POST
def refund_payment(request, transaction_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    """
    Refund a transaction.
    
    POST /api/payments/transactions/<transaction_id>/refund
    
    Request body (optional):
        {
            "amount": 5000  # Amount to refund (if None, full refund)
        }
    
    Response:
        {
            "success": bool,
            "refund_id": str,
            "amount": int,
            "error": str (if not successful)
        }
    """
    
    try:
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        
        # Verify user owns the order
        if transaction.order.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}
        
        amount = data.get('amount')
        
        result = PaymentService.refund_transaction(
            transaction_id=transaction_id,
            amount=amount,
            actor=f'user_{request.user.id}'
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
    
    except Exception as e:
        logger.error(f"Error in refund: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def webhook_bereke(request):
    """
    Bereke Bank webhook callback.
    
    POST /api/payments/webhook/bereke
    
    Validates signature and processes payment updates.
    Returns HTTP 200 immediately; updates processed asynchronously.
    """
    
    try:
        # Get signature from header
        signature = request.META.get('HTTP_X_BEREKE_SIGNATURE', '')
        
        # Get raw body
        payload = request.body
        
        # Validate signature
        client = BereкeBankClient()
        if not client.validate_webhook_signature(payload, signature):
            logger.warning("Invalid Bereke webhook signature")
            # Return 200 anyway to not trigger retries
            return JsonResponse({'status': 'ok'})
        
        # Parse payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Bereke webhook")
            return JsonResponse({'status': 'ok'})
        
        # Extract transaction ID and status
        transaction_id = data.get('transactionId')
        status = data.get('status')  # PAID, FAILED, REFUNDED
        
        if not transaction_id:
            logger.error("Missing transactionId in Bereke webhook")
            return JsonResponse({'status': 'ok'})
        
        # Update transaction status
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            
            # Normalize status
            status_map = {'PAID': 'completed', 'FAILED': 'failed', 'REFUNDED': 'refunded'}
            normalized_status = status_map.get(status, 'pending')
            
            if normalized_status != transaction.status:
                transaction.status = normalized_status
                transaction.metadata.update(data)
                
                if normalized_status == 'completed':
                    from django.utils import timezone
                    transaction.completed_at = timezone.now()
                    transaction.order.transition_to('paid', actor='webhook')
                    if transaction.metadata.get('is_subscription') or 'subscription' in transaction.order.description.lower():
                        PaymentService.activate_subscription_for_user(transaction.order.user)
                elif normalized_status == 'failed':
                    transaction.order.transition_to('failed', actor='webhook')
                
                transaction.save()
                
                logger.info(f"[WEBHOOK] Bereke transaction updated: {transaction_id} → {normalized_status}")
        
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found in webhook: {transaction_id}")
        
        # Return 200 immediately
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"Bereke webhook error: {str(e)}")
        # Return 200 to not trigger provider retries
        return JsonResponse({'status': 'ok'})


@csrf_exempt
@require_POST
def webhook_paypal(request):
    """
    PayPal webhook callback.
    
    POST /api/payments/webhook/paypal
    
    Validates signature and processes payment updates.
    Returns HTTP 200 immediately; updates processed asynchronously.
    """
    
    try:
        # Get signature from header
        signature = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG', '')
        
        # Get raw body
        payload = request.body
        
        # Validate signature (simplified - real implementation uses PayPal API)
        client = PayPalClient()
        if not client.validate_webhook_signature(payload, signature):
            logger.warning("Invalid PayPal webhook signature")
            return JsonResponse({'status': 'ok'})
        
        # Parse payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in PayPal webhook")
            return JsonResponse({'status': 'ok'})
        
        # Extract order ID and event type
        event_type = data.get('event_type')
        resource = data.get('resource', {})
        
        if event_type == 'CHECKOUT.ORDER.COMPLETED':
            order_id = resource.get('id')
            
            # Find transaction by PayPal order ID in metadata
            try:
                transaction = Transaction.objects.get(
                    metadata__paypal_order_id=order_id
                )
                
                transaction.status = 'completed'
                transaction.metadata.update({'paypal_status': 'COMPLETED'})
                transaction.completed_at = datetime.now(timezone.utc)
                transaction.save()
                
                transaction.order.transition_to('paid', actor='webhook')
                if transaction.metadata.get('is_subscription') or 'subscription' in transaction.order.description.lower():
                    PaymentService.activate_subscription_for_user(transaction.order.user)
                
                logger.info(f"[WEBHOOK] PayPal order completed: {order_id}")
            
            except Transaction.DoesNotExist:
                logger.error(f"PayPal order not found: {order_id}")
        
        # Return 200 immediately
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"PayPal webhook error: {str(e)}")
        return JsonResponse({'status': 'ok'})


# ==================== PAYMENT PAGES ====================

@login_required
def paypal_payment_page(request):
    """
    Display PayPal payment page.
    
    GET /payments/paypal/
    Query params:
        - amount: Payment amount in USD (default: 10)
        - description: Order description (default: "Service Payment")
        - currency: Currency code (default: USD)
    """
    
    try:
        logger.info(f'[PAYMENT PAGE] Rendering for user: {request.user.username if request.user.is_authenticated else "anonymous"}')
        
        # Get PayPal Client ID from environment
        paypal_client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
        paypal_sandbox = os.environ.get('PAYPAL_SANDBOX', 'true').lower() == 'true'
        
        logger.info(f'[PAYMENT PAGE] Config: sandbox={paypal_sandbox}, client_id_set={bool(paypal_client_id)}')
        
        if not paypal_client_id:
            error_msg = 'PayPal not configured - PAYPAL_CLIENT_ID environment variable missing'
            logger.error(f'[PAYMENT PAGE] ✗ {error_msg}')
            return render(request, 'payments/error.html', {
                'error': error_msg,
                'details': 'Contact support to enable PayPal payments.'
            }, status=500)
        
        # Get payment parameters from query string
        amount = request.GET.get('amount', '10')
        description = request.GET.get('description', 'Service Payment')
        currency = request.GET.get('currency', 'USD')
        
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0 or amount_float > 999999:
                return render(request, 'payments/error.html', {
                    'error': 'Invalid payment amount. Please enter a value between 0.01 and 999999.'
                }, status=400)
        except ValueError:
            return render(request, 'payments/error.html', {
                'error': 'Invalid payment amount format.'
            }, status=400)
        
        # Convert to cents for backend (if needed)
        amount_cents = int(amount_float * 100)
        
        context = {
            'paypal_client_id': paypal_client_id,
            'amount': amount,
            'amount_cents': amount_cents,
            'currency': currency,
            'order_description': description,
            'user': request.user,
        }
        
        return render(request, 'payments/paypal_payment.html', context)
    
    except Exception as e:
        logger.error(f"Error displaying PayPal payment page: {str(e)}")
        return render(request, 'payments/error.html', {
            'error': 'An error occurred. Please try again later.'
        }, status=500)


@login_required
def payment_success(request):
    """
    Payment success page.
    
    GET /payments/success/
    Query params:
        - order_id: Order ID (optional)
        - transaction_id: Transaction ID (optional)
    """
    
    order_id = request.GET.get('order_id')
    transaction_id = request.GET.get('transaction_id')
    
    context = {
        'order_id': order_id,
        'transaction_id': transaction_id,
    }
    
    # Try to fetch order details if order_id provided
    if order_id:
        try:
            order = get_object_or_404(Order, id=order_id, user=request.user)
            transactions = order.transactions.all()
            context['order'] = order
            context['transactions'] = transactions
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
    
    return render(request, 'payments/success.html', context)


@login_required
def payment_error(request):
    """
    Payment error page.
    
    GET /payments/error/
    Query params:
        - error_code: Error code (optional)
        - error_message: Error message (optional)
    """
    
    error_code = request.GET.get('error_code', 'UNKNOWN_ERROR')
    error_message = request.GET.get('error_message', 'An unexpected error occurred')
    
    context = {
        'error_code': error_code,
        'error_message': error_message,
    }
    
    return render(request, 'payments/error.html', context)
