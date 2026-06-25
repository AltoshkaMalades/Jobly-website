"""
Payment dashboard views.
"""
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from datetime import timedelta
from django.utils import timezone

from payments.models import Order, Transaction
from payments.saas_metrics import (
    conversion_rate_over_time,
    current_active_mrr,
    rolling_30_day_churn,
)

logger = logging.getLogger(__name__)


@login_required
@require_GET
def payment_history(request):
    """
    Display user's payment history and transaction details.
    
    GET /payments/history/
    Query params:
        - page: Page number (default: 1)
        - status: Filter by order status (pending, paid, failed, refunded)
    """
    
    try:
        logger.info(f"[DASHBOARD] Payment history for user: {request.user.username}")
        
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        
        # Get user's orders
        orders_query = Order.objects.filter(user=request.user).select_related('user').prefetch_related('transactions')
        
        # Apply status filter
        if status_filter and status_filter in ['pending', 'paid', 'failed', 'refunded']:
            orders_query = orders_query.filter(status=status_filter)
        
        # Sort by most recent first
        orders = orders_query.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(orders, 10)  # 10 items per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Calculate statistics
        total_spent = Order.objects.filter(
            user=request.user,
            status='paid'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_transactions = Transaction.objects.filter(
            order__user=request.user
        ).count()
        
        pending_orders = Order.objects.filter(
            user=request.user,
            status='pending'
        ).count()
        
        # Recent stats (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_spent = Order.objects.filter(
            user=request.user,
            status='paid',
            created_at__gte=thirty_days_ago
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        context = {
            'page_obj': page_obj,
            'orders': page_obj.object_list,
            'total_pages': paginator.num_pages,
            'total_spent': total_spent / 100,  # Convert from cents
            'total_transactions': total_transactions,
            'pending_orders': pending_orders,
            'recent_spent': recent_spent / 100,  # Convert from cents
            'status_filter': status_filter,
            'available_statuses': [
                ('pending', '⏳ Pending'),
                ('paid', '✅ Paid'),
                ('failed', '❌ Failed'),
                ('refunded', '🔄 Refunded'),
            ],
        }
        
        logger.info(f"[DASHBOARD] Loaded {len(page_obj.object_list)} orders for user")
        return render(request, 'payments/payment_history.html', context)
    
    except Exception as e:
        logger.error(f"[DASHBOARD] Error loading payment history: {str(e)}")
        return render(request, 'payments/error.html', {
            'error': 'Error loading payment history',
            'details': str(e)
        }, status=500)


@login_required
@require_GET
def order_details(request, order_id):
    """
    Display detailed information about a specific order.
    
    GET /payments/orders/<order_id>/
    """
    
    try:
        # Get order (ensure user owns it)
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Get related transactions
        transactions = order.transactions.all().order_by('-created_at')
        
        logger.info(f"[DASHBOARD] Viewing order {order_id} for user: {request.user.username}")
        
        context = {
            'order': order,
            'transactions': transactions,
            'total_amount': order.amount / 100,
            'status_display': dict([
                ('pending', '⏳ Pending'),
                ('paid', '✅ Paid'),
                ('failed', '❌ Failed'),
                ('refunded', '🔄 Refunded'),
            ]).get(order.status, order.status),
        }
        
        return render(request, 'payments/order_details.html', context)
    
    except Exception as e:
        logger.error(f"[DASHBOARD] Error loading order details: {str(e)}")
        return render(request, 'payments/error.html', {
            'error': 'Order not found',
            'details': 'The order you requested does not exist or you do not have access to it.'
        }, status=404)


@login_required
@require_GET
def payment_stats(request):
    """
    Display payment statistics for current user.
    
    GET /payments/stats/
    """
    
    try:
        logger.info(f"[DASHBOARD] Payment stats for user: {request.user.username}")
        
        # All time stats
        all_orders = Order.objects.filter(user=request.user)
        all_paid = all_orders.filter(status='paid')
        
        total_spent = all_paid.aggregate(Sum('amount'))['amount__sum'] or 0
        total_paid_orders = all_paid.count()
        total_pending = all_orders.filter(status='pending').count()
        total_failed = all_orders.filter(status='failed').count()
        
        # Monthly stats
        month_ago = timezone.now() - timedelta(days=30)
        month_spent = all_paid.filter(created_at__gte=month_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        month_orders = all_paid.filter(created_at__gte=month_ago).count()
        
        # By provider stats
        by_provider = Transaction.objects.filter(
            order__user=request.user
        ).values('provider').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        provider_stats = [{
            'provider': item['provider'],
            'count': item['count'],
            'total': (item['total'] or 0) / 100,
        } for item in by_provider]
        
        context = {
            'total_spent': total_spent / 100,
            'total_paid_orders': total_paid_orders,
            'total_pending': total_pending,
            'total_failed': total_failed,
            'month_spent': month_spent / 100,
            'month_orders': month_orders,
            'provider_stats': provider_stats,
            'avg_order_value': (total_spent / total_paid_orders / 100) if total_paid_orders > 0 else 0,
        }
        
        return render(request, 'payments/payment_stats.html', context)
    
    except Exception as e:
        logger.error(f"[DASHBOARD] Error loading payment stats: {str(e)}")
        return render(request, 'payments/error.html', {
            'error': 'Error loading statistics',
            'details': str(e)
        }, status=500)


@login_required
@require_GET
def saas_metrics(request):
    """Show SaaS KPI metrics from subscription and payment history."""
    # Call each metric query separately and continue rendering even if one fails.
    errors = []
    conversion = []
    mrr = {}
    churn = {}

    try:
        try:
            conversion = conversion_rate_over_time()
        except Exception as e:
            logger.exception("[DASHBOARD] conversion_rate_over_time() failed")
            errors.append(f"conversion: {str(e)}")
            conversion = []

        try:
            mrr = current_active_mrr()
        except Exception as e:
            logger.exception("[DASHBOARD] current_active_mrr() failed")
            errors.append(f"mrr: {str(e)}")
            mrr = {}

        try:
            churn = rolling_30_day_churn()
        except Exception as e:
            logger.exception("[DASHBOARD] rolling_30_day_churn() failed")
            errors.append(f"churn: {str(e)}")
            churn = {}

        revenue_at_start = float((churn.get('revenue_at_start_minor_units') or 0)) / 100.0
        churned_revenue = float((churn.get('churned_revenue_minor_units') or 0)) / 100.0

        context = {
            'conversion_rate': conversion,
            'active_subscribers': mrr.get('active_subscribers', 0) or 0,
            'current_active_mrr': float(mrr.get('current_active_mrr_major_units') or 0),
            'user_churn_pct': churn.get('user_churn_pct') or 0,
            'revenue_churn_pct': churn.get('revenue_churn_pct') or 0,
            'revenue_at_start': revenue_at_start,
            'churned_revenue': churned_revenue,
            'churned_customer_count': churn.get('churned_customer_count') or 0,
            'start_customer_count': churn.get('start_customer_count') or 0,
            'end_customer_count': churn.get('end_customer_count') or 0,
            'errors': errors,
        }

        return render(request, 'payments/saas_metrics.html', context)

    except Exception as e:
        logger.exception(f"[DASHBOARD] Unexpected error loading SaaS metrics: {str(e)}")
        return render(request, 'payments/error.html', {
            'error': 'Failed to load SaaS metrics',
            'details': str(e)
        }, status=500)
