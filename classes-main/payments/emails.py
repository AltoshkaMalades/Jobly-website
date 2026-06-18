"""
Email service for payment notifications.
"""
import logging
from typing import Dict, Any, Optional
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class PaymentEmailService:
    """Service for sending payment-related emails."""
    
    @staticmethod
    def send_payment_receipt(
        user,
        order,
        transaction=None,
        provider: str = 'paypal',
    ) -> bool:
        """
        Send payment receipt email to user.
        
        Args:
            user: Django User object
            order: Order model instance
            transaction: Transaction model instance (optional)
            provider: Payment provider name (paypal, bereke, etc.)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            logger.info(f"[EMAIL] Sending payment receipt to {user.email} for order {order.id}")
            
            # Prepare context
            context = {
                'user': user,
                'order': order,
                'transaction_id': transaction.transaction_id if transaction else None,
                'amount': f"{order.amount / 100:.2f}",
                'provider': provider,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://jobaggreator.com',
            }
            
            # Render email templates
            subject = _("💳 Payment Receipt - Order #{}").format(order.id)
            text_content = render_to_string('emails/payment_receipt.txt', context)
            html_content = render_to_string('emails/payment_receipt.html', context)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            result = email.send()
            
            if result > 0:
                logger.info(f"[EMAIL] ✓ Payment receipt sent to {user.email}")
                return True
            else:
                logger.warning(f"[EMAIL] ✗ Failed to send payment receipt to {user.email}")
                return False
        
        except Exception as e:
            logger.error(f"[EMAIL] ✗ Error sending payment receipt: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_error_notification(
        user,
        order,
        error_message: str = None,
    ) -> bool:
        """
        Send payment error notification to user.
        
        Args:
            user: Django User object
            order: Order model instance
            error_message: Error description
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            logger.info(f"[EMAIL] Sending error notification to {user.email} for order {order.id}")
            
            subject = _("❌ Payment Failed - Order #{}").format(order.id)
            
            text_content = f"""
Dear {user.first_name or user.username},

Unfortunately, your payment for order #{order.id} could not be processed.

Order Details:
- Amount: ${order.amount / 100:.2f} {order.currency}
- Description: {order.description}
- Date: {order.created_at.strftime('%d.%m.%Y %H:%M')}

Error Details:
{error_message or 'Technical error occurred during payment processing.'}

Please try again or contact our support team at support@jobaggreator.com

Best regards,
JobAggregator Team
© 2026 JobAggregator. All rights reserved.
"""
            
            html_content = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>❌ Payment Failed</h2>
    <p>Dear {user.first_name or user.username},</p>
    <p>Unfortunately, your payment for order #{order.id} could not be processed.</p>
    
    <h3>Order Details:</h3>
    <ul>
        <li><strong>Amount:</strong> ${order.amount / 100:.2f} {order.currency}</li>
        <li><strong>Description:</strong> {order.description}</li>
        <li><strong>Date:</strong> {order.created_at.strftime('%d.%m.%Y %H:%M')}</li>
    </ul>
    
    <h3>Error Details:</h3>
    <p>{error_message or 'Technical error occurred during payment processing.'}</p>
    
    <p>Please try again or contact our support team at <a href="mailto:support@jobaggreator.com">support@jobaggreator.com</a></p>
    
    <p>Best regards,<br>JobAggregator Team</p>
    <p style="color: #999; font-size: 12px;">© 2026 JobAggregator. All rights reserved.</p>
</body>
</html>
"""
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            result = email.send()
            
            if result > 0:
                logger.info(f"[EMAIL] ✓ Error notification sent to {user.email}")
                return True
            else:
                logger.warning(f"[EMAIL] ✗ Failed to send error notification to {user.email}")
                return False
        
        except Exception as e:
            logger.error(f"[EMAIL] ✗ Error sending payment error notification: {str(e)}")
            return False
    
    @staticmethod
    def send_admin_payment_notification(
        order,
        transaction=None,
        status: str = 'completed',
    ) -> bool:
        """
        Send admin notification about payment.
        
        Args:
            order: Order model instance
            transaction: Transaction model instance (optional)
            status: Payment status (completed, failed, pending)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            admin_email = getattr(settings, 'ADMIN_EMAIL', None)
            if not admin_email:
                logger.debug("[EMAIL] Admin email not configured, skipping admin notification")
                return False
            
            logger.info(f"[EMAIL] Sending admin notification for order {order.id}")
            
            subject = f"[{status.upper()}] Payment Notification - Order #{order.id}"
            
            text_content = f"""
Payment Notification

Status: {status.upper()}
Order ID: {order.id}
User: {order.user.email}
Amount: ${order.amount / 100:.2f} {order.currency}
Description: {order.description}
Created: {order.created_at.strftime('%d.%m.%Y %H:%M')}

{f'Transaction ID: {transaction.transaction_id}' if transaction else ''}
{f'Provider: {transaction.provider}' if transaction else ''}

View in admin: https://jobaggreator.com/admin/payments/order/{order.id}/
"""
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email]
            )
            
            result = email.send()
            
            if result > 0:
                logger.info(f"[EMAIL] ✓ Admin notification sent")
                return True
            else:
                logger.warning(f"[EMAIL] ✗ Failed to send admin notification")
                return False
        
        except Exception as e:
            logger.error(f"[EMAIL] ✗ Error sending admin notification: {str(e)}")
            return False
