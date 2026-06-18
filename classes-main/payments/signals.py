"""
Payment signals for email notifications.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import logging

from payments.models import Order, Transaction
from payments.emails import PaymentEmailService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def send_payment_receipt_email(sender, instance: Transaction, created=False, **kwargs):
    """
    Send payment receipt email when transaction is completed.
    
    Triggered when a Transaction is saved with status='completed'.
    """
    try:
        # Only send email if transaction status changed to completed
        if instance.status != 'completed':
            logger.debug(f"[SIGNAL] Skipping email for transaction {instance.id} with status {instance.status}")
            return
        
        # Check if email was already sent (check metadata)
        if instance.metadata.get('receipt_email_sent'):
            logger.debug(f"[SIGNAL] Receipt email already sent for transaction {instance.id}")
            return
        
        logger.info(f"[SIGNAL] Payment completed, sending receipt email for transaction {instance.id}")
        
        # Get order and user
        order = instance.order
        user = order.user
        
        # Send receipt email
        success = PaymentEmailService.send_payment_receipt(
            user=user,
            order=order,
            transaction=instance,
            provider=instance.provider
        )
        
        # Send admin notification
        PaymentEmailService.send_admin_payment_notification(
            order=order,
            transaction=instance,
            status='completed'
        )
        
        # Mark email as sent in transaction metadata
        if success:
            instance.metadata['receipt_email_sent'] = True
            instance.metadata['receipt_email_sent_at'] = timezone.now().isoformat()
            instance.save(update_fields=['metadata'])
            logger.info(f"[SIGNAL] ✓ Receipt email sent for transaction {instance.id}")
        else:
            logger.warning(f"[SIGNAL] ✗ Failed to send receipt email for transaction {instance.id}")
    
    except Exception as e:
        logger.error(f"[SIGNAL] ✗ Error in send_payment_receipt_email: {str(e)}")


@receiver(post_save, sender=Transaction)
def send_payment_error_notification(sender, instance: Transaction, created=False, **kwargs):
    """
    Send error notification when transaction fails.
    
    Triggered when a Transaction is saved with status='failed'.
    """
    try:
        # Only send email if transaction status changed to failed
        if instance.status != 'failed':
            return
        
        # Check if error email was already sent
        if instance.metadata.get('error_email_sent'):
            logger.debug(f"[SIGNAL] Error email already sent for transaction {instance.id}")
            return
        
        logger.info(f"[SIGNAL] Payment failed, sending error notification for transaction {instance.id}")
        
        # Get order and user
        order = instance.order
        user = order.user
        
        # Get error message from metadata
        error_message = instance.metadata.get('error_message', 'Payment processing failed. Please try again.')
        
        # Send error email
        success = PaymentEmailService.send_payment_error_notification(
            user=user,
            order=order,
            error_message=error_message
        )
        
        # Send admin notification
        PaymentEmailService.send_admin_payment_notification(
            order=order,
            transaction=instance,
            status='failed'
        )
        
        # Mark email as sent
        if success:
            instance.metadata['error_email_sent'] = True
            instance.metadata['error_email_sent_at'] = timezone.now().isoformat()
            instance.save(update_fields=['metadata'])
            logger.info(f"[SIGNAL] ✓ Error notification sent for transaction {instance.id}")
        else:
            logger.warning(f"[SIGNAL] ✗ Failed to send error notification for transaction {instance.id}")
    
    except Exception as e:
        logger.error(f"[SIGNAL] ✗ Error in send_payment_error_notification: {str(e)}")
