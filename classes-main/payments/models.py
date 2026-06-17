from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


# ==================== ORDER STATUSES ====================
ORDER_STATUS_CHOICES = [
    ('created', 'Created'),
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('fulfilled', 'Fulfilled'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
]

# Valid state transitions: From → [To, ...]
VALID_STATE_TRANSITIONS = {
    'created': ['pending', 'failed'],
    'pending': ['paid', 'failed'],
    'paid': ['fulfilled', 'refunded'],
    'fulfilled': ['completed'],
    'completed': [],
    'failed': [],
    'refunded': [],
}


# ==================== ORDER MODEL ====================
class Order(models.Model):
    """Order for a service or product purchase."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='created',
        db_index=True,
        help_text='Current order status'
    )
    
    # Order details
    amount = models.BigIntegerField(
        help_text='Amount in minor units (cents/tiyn) to avoid float precision issues'
    )
    currency = models.CharField(max_length=3, default='KZT', help_text='ISO 4217 currency code')
    description = models.TextField(blank=True, help_text='Order description')
    
    # Idempotency
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Unique key to prevent duplicate charges'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['idempotency_key']),
        ]
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.status})"
    
    def can_transition_to(self, new_status):
        """Check if transition from current status to new_status is valid."""
        if new_status not in dict(ORDER_STATUS_CHOICES):
            return False
        valid_targets = VALID_STATE_TRANSITIONS.get(self.status, [])
        return new_status in valid_targets
    
    def transition_to(self, new_status, actor='system'):
        """
        Transition order to new status with validation and logging.
        
        Args:
            new_status: Target status
            actor: Who initiated the transition (user, system, webhook, etc.)
        
        Raises:
            ValidationError: If transition is not allowed
        """
        if not self.can_transition_to(new_status):
            raise ValidationError(
                f"Cannot transition from '{self.status}' to '{new_status}'"
            )
        
        old_status = self.status
        self.status = new_status
        self.save()
        
        # Log transition
        StateTransitionLog.objects.create(
            order=self,
            from_status=old_status,
            to_status=new_status,
            actor=actor
        )
        
        logger.info(
            f"[ORDER] Status transition | Order: {self.id} | "
            f"{old_status} → {new_status} | Actor: {actor}"
        )


# ==================== TRANSACTION MODEL ====================
class Transaction(models.Model):
    """Payment transaction record."""
    
    PROVIDER_CHOICES = [
        ('bereke', 'Bereke Bank'),
        ('paypal', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction identifiers
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Provider transaction ID'
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        help_text='Payment provider'
    )
    
    # Status and amounts
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    amount = models.BigIntegerField(
        help_text='Amount in minor units (cents/tiyn)'
    )
    currency = models.CharField(max_length=3, default='KZT')
    
    # Idempotency
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Prevent duplicate submissions'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional provider-specific data'
    )
    
    # Refund info
    refund_amount = models.BigIntegerField(
        default=0,
        help_text='Amount refunded in minor units'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['idempotency_key']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} ({self.provider}) - {self.status}"


# ==================== STATE TRANSITION LOG ====================
class StateTransitionLog(models.Model):
    """Audit log for order state transitions."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='transition_logs'
    )
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    actor = models.CharField(
        max_length=100,
        help_text='Who triggered the transition (user, system, webhook, etc.)'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'State Transition Log'
        verbose_name_plural = 'State Transition Logs'
        indexes = [
            models.Index(fields=['order', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Order {self.order.id}: {self.from_status} → {self.to_status}"
