"""
KPI Dashboard views for payment and business metrics.
Exposes internal API for analytics dashboards.
"""
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, Case, When, DecimalField
from django.utils import timezone

from payments.models import Order, Transaction

logger = logging.getLogger(__name__)


@csrf_exempt
@require_GET
def kpi_dashboard(request):
    """
    Internal KPI dashboard API.
    Returns payment metrics: revenue, conversion rate, MRR, payment success, refunds.
    
    Query Parameters:
        period: 'today', 'week', 'month', 'all' (default: 'month')
    
    GET /api/kpi/dashboard/?period=month
    
    Response:
        {
            "period": "month",
            "timestamp": "2026-06-16T10:30:00Z",
            "metrics": {
                "total_revenue": 5000000,           // in minor units
                "successful_payments": 42,
                "failed_payments": 3,
                "payment_success_rate": 93.33,      // percentage
                "total_refunds": 500000,            // in minor units
                "refund_count": 2,
                "refund_rate": 4.76,                // % of paid orders
                "mrr": 1234567,                     // Monthly Recurring Revenue (estimated)
                "average_order_value": 119047,      // in minor units
                "unique_customers": 42,
                "orders": {
                    "created": 45,
                    "pending": 2,
                    "paid": 40,
                    "fulfilled": 38,
                    "completed": 35,
                    "failed": 3,
                    "refunded": 2
                },
                "providers": {
                    "bereke": {
                        "count": 22,
                        "revenue": 2500000,
                        "success_rate": 95.45
                    },
                    "paypal": {
                        "count": 20,
                        "revenue": 2500000,
                        "success_rate": 90.00
                    }
                }
            }
        }
    """
    
    try:
        period = request.GET.get('period', 'month')
        now = timezone.now()
        
        # Determine date range
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:  # 'all'
            start_date = datetime.min.replace(tzinfo=timezone.utc)
        
        # Query data
        orders = Order.objects.filter(created_at__gte=start_date)
        transactions = Transaction.objects.filter(created_at__gte=start_date)
        
        # Basic metrics
        total_orders = orders.count()
        unique_customers = orders.values('user_id').distinct().count()
        
        # Revenue metrics
        paid_transactions = transactions.filter(status='completed')
        total_revenue = paid_transactions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        refunded_transactions = transactions.filter(status='refunded')
        total_refunds = refunded_transactions.aggregate(
            total=Sum('refund_amount')
        )['total'] or 0
        
        # Payment success metrics
        completed_count = paid_transactions.count()
        failed_transactions = transactions.filter(status='failed')
        failed_count = failed_transactions.count()
        total_transactions = transactions.count()
        
        success_rate = (
            (completed_count / total_transactions * 100) if total_transactions > 0 else 0
        )
        
        # Refund metrics
        paid_orders_count = orders.filter(status__in=['paid', 'fulfilled', 'completed']).count()
        refund_rate = (
            (refunded_transactions.count() / paid_orders_count * 100) 
            if paid_orders_count > 0 else 0
        )
        
        # Average order value
        average_order = (
            (total_revenue / completed_count) if completed_count > 0 else 0
        )
        
        # MRR (Monthly Recurring Revenue) - estimate from last month's paid orders
        mrr_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.day == 1:
            mrr_start = (now - timedelta(days=1)).replace(day=1)
        
        mrr_orders = orders.filter(
            created_at__gte=mrr_start,
            status__in=['paid', 'fulfilled', 'completed']
        ).aggregate(
            total=Sum(F('amount'), output_field=DecimalField())
        )['total'] or 0
        
        # Order status breakdown
        order_statuses = {}
        for status_choice in Order._meta.get_field('status').choices:
            status_value = status_choice[0]
            count = orders.filter(status=status_value).count()
            order_statuses[status_value] = count
        
        # Provider breakdown
        provider_metrics = {}
        for provider in ['bereke', 'paypal']:
            provider_txns = transactions.filter(provider=provider)
            provider_count = provider_txns.count()
            provider_revenue = provider_txns.filter(
                status='completed'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            provider_success = provider_txns.filter(status='completed').count()
            provider_total = provider_txns.count()
            provider_success_rate = (
                (provider_success / provider_total * 100) 
                if provider_total > 0 else 0
            )
            
            provider_metrics[provider] = {
                'count': provider_count,
                'revenue': provider_revenue,
                'success_rate': round(provider_success_rate, 2),
            }
        
        return JsonResponse({
            'period': period,
            'timestamp': now.isoformat(),
            'metrics': {
                'total_revenue': int(total_revenue),
                'successful_payments': completed_count,
                'failed_payments': failed_count,
                'payment_success_rate': round(success_rate, 2),
                'total_refunds': int(total_refunds),
                'refund_count': refunded_transactions.count(),
                'refund_rate': round(refund_rate, 2),
                'mrr': int(mrr_orders),
                'average_order_value': int(average_order),
                'unique_customers': unique_customers,
                'orders': order_statuses,
                'providers': provider_metrics,
            }
        })
    
    except Exception as e:
        logger.error(f"KPI dashboard error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch KPI metrics',
            'details': str(e)
        }, status=500)


@login_required
@require_GET
def revenue_by_date(request):
    """
    Revenue breakdown by date.
    
    GET /api/kpi/revenue-by-date/?days=30
    
    Response:
        {
            "data": [
                {
                    "date": "2026-05-17",
                    "revenue": 1000000,
                    "transactions": 10,
                    "refunds": 50000
                },
                ...
            ]
        }
    """
    
    try:
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        daily_revenue = {}
        
        # Get completed transactions
        txns = Transaction.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).values('created_at__date').annotate(
            revenue=Sum('amount'),
            count=Count('id')
        )
        
        for txn in txns:
            date_str = txn['created_at__date'].isoformat()
            daily_revenue[date_str] = {
                'revenue': txn['revenue'],
                'transactions': txn['count'],
                'refunds': 0,
            }
        
        # Get refunds
        refunds = Transaction.objects.filter(
            created_at__gte=start_date,
            status='refunded'
        ).values('created_at__date').annotate(
            refund_total=Sum('refund_amount')
        )
        
        for refund in refunds:
            date_str = refund['created_at__date'].isoformat()
            if date_str not in daily_revenue:
                daily_revenue[date_str] = {
                    'revenue': 0,
                    'transactions': 0,
                    'refunds': refund['refund_total'],
                }
            else:
                daily_revenue[date_str]['refunds'] = refund['refund_total']
        
        # Sort by date
        sorted_data = [
            {'date': date, **metrics}
            for date, metrics in sorted(daily_revenue.items())
        ]
        
        return JsonResponse({'data': sorted_data})
    
    except Exception as e:
        logger.error(f"Revenue by date error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch revenue data',
            'details': str(e)
        }, status=500)


@login_required
@require_GET
def conversion_funnel(request):
    """
    Conversion funnel: Orders created → Paid → Fulfilled → Completed
    
    GET /api/kpi/conversion-funnel/?days=30
    
    Response:
        {
            "funnel": [
                {"stage": "created", "count": 100, "percentage": 100},
                {"stage": "pending", "count": 95, "percentage": 95},
                {"stage": "paid", "count": 90, "percentage": 90},
                {"stage": "fulfilled", "count": 85, "percentage": 85},
                {"stage": "completed", "count": 80, "percentage": 80}
            ]
        }
    """
    
    try:
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        orders = Order.objects.filter(created_at__gte=start_date)
        total_orders = orders.count()
        
        if total_orders == 0:
            return JsonResponse({'funnel': []})
        
        stages = ['created', 'pending', 'paid', 'fulfilled', 'completed']
        funnel = []
        
        for stage in stages:
            stage_count = orders.filter(status=stage).count()
            percentage = (stage_count / total_orders * 100)
            
            funnel.append({
                'stage': stage,
                'count': stage_count,
                'percentage': round(percentage, 2),
            })
        
        return JsonResponse({'funnel': funnel})
    
    except Exception as e:
        logger.error(f"Conversion funnel error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch funnel data',
            'details': str(e)
        }, status=500)
