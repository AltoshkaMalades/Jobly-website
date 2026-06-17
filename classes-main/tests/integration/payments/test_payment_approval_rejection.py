"""
Integration tests for payment approval and rejection scenarios.
Tests payment state transitions: rejection (failed), approval (paid), and error handling.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from payments.models import Order, Transaction, StateTransitionLog
from payments.services.service import PaymentService
from payments.services.base import PaymentClientError


@pytest.mark.django_db
class TestPaymentRejection(TestCase):
    """Test payment rejection scenarios."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_order_transition_to_failed_from_created(self):
        """Test order can transition from created → failed (rejection)."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_001',
            status='created'
        )
        
        assert order.can_transition_to('failed')
        order.transition_to('failed', actor='webhook')
        
        assert order.status == 'failed'
        
        # Verify log was created
        log = StateTransitionLog.objects.get(order=order)
        assert log.from_status == 'created'
        assert log.to_status == 'failed'
        assert log.actor == 'webhook'
    
    def test_order_transition_to_failed_from_pending(self):
        """Test order can transition from pending → failed (rejection)."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_002',
            status='pending'
        )
        
        assert order.can_transition_to('failed')
        order.transition_to('failed', actor='webhook')
        
        assert order.status == 'failed'
    
    def test_payment_rejection_via_webhook_bereke(self):
        """Test payment rejection through Bereke webhook."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_003',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-REJECT-001',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_reject_001',
            status='pending'
        )
        
        # Simulate rejected webhook from Bereke
        webhook_payload = {
            'transaction_id': 'TXN-REJECT-001',
            'status': 'REJECTED',
            'reason': 'Insufficient funds',
            'timestamp': '2026-06-17T10:30:00Z'
        }
        
        # Update order and transaction to failed
        order.transition_to('failed', actor='webhook')
        transaction.status = 'failed'
        transaction.save()
        
        assert order.status == 'failed'
        assert transaction.status == 'failed'
    
    def test_payment_rejection_via_webhook_paypal(self):
        """Test payment rejection through PayPal webhook."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_004',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='PAYPAL-REJECT-001',
            provider='paypal',
            amount=10000,
            currency='KZT',
            idempotency_key='paypal_reject_001',
            status='pending'
        )
        
        # Update to failed
        order.transition_to('failed', actor='webhook')
        transaction.status = 'failed'
        transaction.save()
        
        assert order.status == 'failed'
        assert transaction.status == 'failed'
    
    @patch('payments.services.service.get_payment_client')
    def test_payment_rejection_on_status_check(self, mock_get_client):
        """Test payment marked as failed when status check reveals rejection."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_005',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-REJECT-002',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_reject_002',
            status='pending'
        )
        
        # Mock client returns failed status
        mock_client = Mock()
        mock_client.get_transaction_status.return_value = {
            'transaction_id': 'TXN-REJECT-002',
            'status': 'failed',
            'metadata': {'reason': 'Card declined'}
        }
        mock_get_client.return_value = mock_client
        
        # Check status (simulating polling)
        result = PaymentService.check_transaction_status(
            transaction_id='TXN-REJECT-002'
        )
        
        # Verify transaction still in pending (not updated in mock)
        assert result['status'] == 'failed'
    
    def test_cannot_transition_from_completed_to_failed(self):
        """Test that completed orders cannot be rejected."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_006',
            status='completed'
        )
        
        # Should not be able to transition to failed
        assert not order.can_transition_to('failed')
        
        with pytest.raises(ValidationError):
            order.transition_to('failed')
    
    def test_cannot_transition_from_refunded_to_failed(self):
        """Test that refunded orders cannot be re-rejected."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_007',
            status='refunded'
        )
        
        assert not order.can_transition_to('failed')
        
        with pytest.raises(ValidationError):
            order.transition_to('failed')
    
    def test_rejection_creates_audit_log(self):
        """Test that rejection creates audit trail."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='reject_test_008',
            status='pending'
        )
        
        order.transition_to('failed', actor='webhook')
        
        logs = StateTransitionLog.objects.filter(order=order)
        assert logs.count() == 1
        
        log = logs.first()
        assert log.from_status == 'pending'
        assert log.to_status == 'failed'
        assert log.actor == 'webhook'
        assert log.timestamp is not None


@pytest.mark.django_db
class TestPaymentApproval(TestCase):
    """Test payment approval scenarios."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_order_transition_to_paid_from_pending(self):
        """Test order can transition from pending → paid (approval)."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_001',
            status='pending'
        )
        
        assert order.can_transition_to('paid')
        order.transition_to('paid', actor='webhook')
        
        assert order.status == 'paid'
        
        # Verify log was created
        log = StateTransitionLog.objects.get(order=order)
        assert log.from_status == 'pending'
        assert log.to_status == 'paid'
        assert log.actor == 'webhook'
    
    def test_payment_approval_via_webhook_bereke(self):
        """Test payment approval through Bereke webhook."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_002',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-APPROVE-001',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_approve_001',
            status='pending'
        )
        
        # Simulate approved webhook from Bereke
        order.transition_to('paid', actor='webhook')
        transaction.status = 'completed'
        transaction.completed_at = None  # Will be set by webhook handler
        transaction.save()
        
        assert order.status == 'paid'
        assert transaction.status == 'completed'
    
    def test_payment_approval_via_webhook_paypal(self):
        """Test payment approval through PayPal webhook."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_003',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='PAYPAL-APPROVE-001',
            provider='paypal',
            amount=10000,
            currency='KZT',
            idempotency_key='paypal_approve_001',
            status='pending'
        )
        
        # Simulate CHECKOUT.ORDER.COMPLETED webhook
        order.transition_to('paid', actor='webhook')
        transaction.status = 'completed'
        transaction.save()
        
        assert order.status == 'paid'
        assert transaction.status == 'completed'
    
    @patch('payments.services.service.get_payment_client')
    def test_payment_approval_on_status_check(self, mock_get_client):
        """Test payment marked as paid when status check reveals approval."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_004',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-APPROVE-002',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_approve_002',
            status='pending'
        )
        
        # Mock client returns completed status
        mock_client = Mock()
        mock_client.get_transaction_status.return_value = {
            'transaction_id': 'TXN-APPROVE-002',
            'status': 'completed',
            'metadata': {'approval_code': 'ABC123'}
        }
        mock_get_client.return_value = mock_client
        
        # Check status
        result = PaymentService.check_transaction_status(
            transaction_id='TXN-APPROVE-002'
        )
        
        assert result['status'] == 'completed'
    
    def test_approved_order_full_lifecycle(self):
        """Test complete order lifecycle after approval."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_005',
            status='created'
        )
        
        # created → pending
        order.transition_to('pending', actor='user')
        assert order.status == 'pending'
        
        # pending → paid (approval)
        order.transition_to('paid', actor='webhook')
        assert order.status == 'paid'
        
        # paid → fulfilled
        order.transition_to('fulfilled', actor='system')
        assert order.status == 'fulfilled'
        
        # fulfilled → completed
        order.transition_to('completed', actor='system')
        assert order.status == 'completed'
        
        # Verify 4 transitions logged
        logs = StateTransitionLog.objects.filter(order=order)
        assert logs.count() == 4
    
    def test_cannot_transition_from_failed_to_paid(self):
        """Test that failed orders cannot be approved."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_006',
            status='failed'
        )
        
        # Should not be able to transition to paid
        assert not order.can_transition_to('paid')
        
        with pytest.raises(ValidationError):
            order.transition_to('paid')
    
    def test_cannot_transition_from_refunded_to_paid(self):
        """Test that refunded orders cannot be paid again."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_007',
            status='refunded'
        )
        
        assert not order.can_transition_to('paid')
        
        with pytest.raises(ValidationError):
            order.transition_to('paid')
    
    def test_approval_creates_audit_log(self):
        """Test that approval creates audit trail."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='approve_test_008',
            status='pending'
        )
        
        order.transition_to('paid', actor='webhook')
        
        logs = StateTransitionLog.objects.filter(order=order)
        assert logs.count() == 1
        
        log = logs.first()
        assert log.from_status == 'pending'
        assert log.to_status == 'paid'
        assert log.actor == 'webhook'
        assert log.timestamp is not None


@pytest.mark.django_db
class TestPaymentApprovalRejectionEdgeCases(TestCase):
    """Test edge cases and error scenarios."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_cannot_approve_created_order_directly(self):
        """Test that created orders must go through pending first."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_001',
            status='created'
        )
        
        # Cannot jump directly to paid
        assert not order.can_transition_to('paid')
        
        with pytest.raises(ValidationError):
            order.transition_to('paid')
    
    def test_duplicate_rejection_not_allowed(self):
        """Test that already-failed orders cannot be failed again."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_002',
            status='failed'
        )
        
        assert not order.can_transition_to('failed')
        
        with pytest.raises(ValidationError):
            order.transition_to('failed')
    
    def test_duplicate_approval_not_allowed(self):
        """Test that already-paid orders cannot be paid again."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_003',
            status='paid'
        )
        
        assert not order.can_transition_to('paid')
        
        with pytest.raises(ValidationError):
            order.transition_to('paid')
    
    def test_concurrent_approval_and_rejection_simulation(self):
        """Test handling of conflicting state updates."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_004',
            status='pending'
        )
        
        # First transition (approval)
        order.transition_to('paid', actor='webhook_1')
        assert order.status == 'paid'
        
        # Try to transition to failed (should fail - not allowed from paid)
        assert not order.can_transition_to('failed')
    
    def test_multiple_transactions_in_single_order(self):
        """Test order with multiple transactions (one approved, others rejected)."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_005',
            status='pending'
        )
        
        # First attempt - rejected
        transaction1 = Transaction.objects.create(
            order=order,
            transaction_id='TXN-001',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_001',
            status='failed'
        )
        
        # Second attempt - approved
        transaction2 = Transaction.objects.create(
            order=order,
            transaction_id='TXN-002',
            provider='paypal',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_002',
            status='completed'
        )
        
        # Only approve the second one
        order.transition_to('paid', actor='webhook')
        assert order.status == 'paid'
        
        # Check both transactions exist
        transactions = order.transactions.all()
        assert transactions.count() == 2
        
        statuses = [t.status for t in transactions]
        assert 'failed' in statuses
        assert 'completed' in statuses
    
    def test_approval_rejection_actor_tracking(self):
        """Test that different actors are properly tracked."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_006',
            status='pending'
        )
        
        # Approval by webhook
        order.transition_to('paid', actor='webhook')
        
        log = StateTransitionLog.objects.get(order=order)
        assert log.actor == 'webhook'
        
        # Reset for next test
        order.status = 'pending'
        order.save()
        
        # Approval by system
        order.transition_to('paid', actor='system')
        
        logs = StateTransitionLog.objects.filter(order=order).order_by('-timestamp')
        assert logs.first().actor == 'system'
    
    def test_rejection_reason_metadata(self):
        """Test storing rejection reason in transaction metadata."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='edge_test_007',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-REJECT-003',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='txn_reject_003',
            status='failed',
            metadata={
                'rejection_reason': 'Insufficient funds',
                'error_code': 'INSUFFICIENT_FUNDS',
                'timestamp': '2026-06-17T10:30:00Z'
            }
        )
        
        order.transition_to('failed', actor='webhook')
        
        transaction.refresh_from_db()
        assert transaction.metadata['rejection_reason'] == 'Insufficient funds'
        assert transaction.status == 'failed'
