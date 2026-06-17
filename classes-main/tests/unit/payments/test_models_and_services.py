"""
Unit tests for payment service and clients.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError

from payments.models import Order, Transaction, StateTransitionLog
from payments.services.service import PaymentService
from payments.services.base import PaymentClientError
from payments.services.bereke import BereкeBankClient
from payments.services.paypal import PayPalClient


@pytest.mark.django_db
class TestOrderModel(TestCase):
    """Test Order model state machine."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_order(self):
        """Test creating an order."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            description='Test order',
            idempotency_key='test_key_001',
            status='created'
        )
        
        assert order.id is not None
        assert order.status == 'created'
        assert order.amount == 10000
    
    def test_valid_state_transition_created_to_pending(self):
        """Test valid state transition: created → pending."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_key_002',
            status='created'
        )
        
        assert order.can_transition_to('pending')
        order.transition_to('pending', actor='system')
        
        assert order.status == 'pending'
        # Check log was created
        assert StateTransitionLog.objects.filter(order=order).count() == 1
    
    def test_invalid_state_transition(self):
        """Test invalid state transition raises error."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_key_003',
            status='created'
        )
        
        assert not order.can_transition_to('refunded')
        
        with pytest.raises(ValidationError):
            order.transition_to('refunded')
    
    def test_full_order_lifecycle(self):
        """Test complete order state machine."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_key_004',
            status='created'
        )
        
        # created → pending
        order.transition_to('pending', actor='user')
        assert order.status == 'pending'
        
        # pending → paid
        order.transition_to('paid', actor='webhook')
        assert order.status == 'paid'
        
        # paid → fulfilled
        order.transition_to('fulfilled', actor='system')
        assert order.status == 'fulfilled'
        
        # fulfilled → completed
        order.transition_to('completed', actor='system')
        assert order.status == 'completed'
        
        # Verify all transitions were logged
        logs = StateTransitionLog.objects.filter(order=order)
        assert logs.count() == 4


@pytest.mark.django_db
class TestTransactionModel(TestCase):
    """Test Transaction model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_key_005',
            status='pending'
        )
    
    def test_create_transaction(self):
        """Test creating a transaction."""
        transaction = Transaction.objects.create(
            order=self.order,
            transaction_id='TXN-001',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='idempotency_001',
            status='pending'
        )
        
        assert transaction.id is not None
        assert transaction.status == 'pending'
        assert transaction.provider == 'bereke'
        assert transaction.refund_amount == 0
    
    def test_idempotency_key_uniqueness(self):
        """Test idempotency key is unique."""
        Transaction.objects.create(
            order=self.order,
            transaction_id='TXN-002',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='idempotency_002',
            status='pending'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Transaction.objects.create(
                order=self.order,
                transaction_id='TXN-003',
                provider='bereke',
                amount=10000,
                currency='KZT',
                idempotency_key='idempotency_002',  # Duplicate
                status='pending'
            )


class TestBereкeBankClient(TestCase):
    """Test Bereke Bank payment client."""
    
    def setUp(self):
        self.client = BereкeBankClient()
    
    def test_create_payment_request_mock_mode(self):
        """Test payment request in mock mode (no API key)."""
        response = self.client.create_payment_request(
            order_id='ORD-001',
            amount=10000,
            currency='KZT',
            return_url='http://localhost:8000/return'
        )
        
        # Mock mode returns payment details directly
        assert 'payment_url' in response
        assert 'transaction_id' in response
        assert response['status'] == 'pending'
        assert response['transaction_id'].startswith('BEREKE-')
    
    def test_normalize_status(self):
        """Test status normalization."""
        assert BereкeBankClient._normalize_status('PAID') == 'completed'
        assert BereкeBankClient._normalize_status('FAILED') == 'failed'
        assert BereкeBankClient._normalize_status('PENDING') == 'pending'
        assert BereкeBankClient._normalize_status('REFUNDED') == 'refunded'
    
    @patch('payments.services.bereke.requests.Session.post')
    def test_signature_validation(self, mock_post):
        """Test webhook signature validation."""
        payload = b'{"test": "data"}'
        
        # Mock mode (no secret) - should return True
        with patch.dict('os.environ', {'BEREKE_API_SECRET': ''}):
            client = BereкeBankClient()
            result = client.validate_webhook_signature(payload, 'any_signature')
            assert result is True


class TestPayPalClient(TestCase):
    """Test PayPal payment client."""
    
    def setUp(self):
        self.client = PayPalClient()
    
    @patch('payments.services.paypal.requests.Session.post')
    def test_create_payment_request_mock_mode(self, mock_post):
        """Test payment request (mocks PayPal API if credentials present)."""
        # Mock PayPal API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 'PAYPAL-abc123',
            'status': 'CREATED',
            'links': [
                {'rel': 'approve', 'href': 'https://sandbox.paypal.com/checkoutnow?token=PAYPAL-abc123'}
            ]
        }
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        response = self.client.create_payment_request(
            order_id='ORD-002',
            amount=10000,
            currency='KZT',
            return_url='http://localhost:8000/return'
        )
        
        # Response should have transaction details
        assert 'payment_url' in response or 'transaction_id' in response
        assert 'status' in response
    
    def test_normalize_status(self):
        """Test PayPal status normalization."""
        assert PayPalClient._normalize_status('COMPLETED') == 'completed'
        assert PayPalClient._normalize_status('CREATED') == 'pending'
        assert PayPalClient._normalize_status('APPROVED') == 'pending'


@pytest.mark.django_db
class TestPaymentService(TestCase):
    """Test payment service."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_idempotency_key_generation(self):
        """Test idempotency key is deterministic."""
        key1 = PaymentService._generate_idempotency_key(1, 'ORD-001', 10000)
        key2 = PaymentService._generate_idempotency_key(1, 'ORD-001', 10000)
        key3 = PaymentService._generate_idempotency_key(1, 'ORD-001', 20000)
        
        assert key1 == key2
        assert key1 != key3
    
    @patch('payments.services.service.get_payment_client')
    def test_create_payment_success(self, mock_get_client):
        """Test successful payment creation."""
        # Mock the payment client
        mock_client = Mock()
        mock_client.create_payment_request.return_value = {
            'payment_url': 'http://example.com/pay',
            'transaction_id': 'TXN-123',
            'status': 'pending',
            'metadata': {}
        }
        mock_get_client.return_value = mock_client
        
        result = PaymentService.create_payment(
            user=self.user,
            order_id='ORD-001',
            amount=10000,
            currency='KZT',
            provider='bereke'
        )
        
        assert result['success'] is True
        assert 'payment_url' in result
        assert 'transaction_id' in result
    
    @patch('payments.services.service.get_payment_client')
    def test_duplicate_payment_detection(self, mock_get_client):
        """Test idempotency - duplicate payments return existing transaction."""
        mock_client = Mock()
        mock_client.create_payment_request.return_value = {
            'payment_url': 'http://example.com/pay',
            'transaction_id': 'TXN-123',
            'status': 'pending',
            'metadata': {}
        }
        mock_get_client.return_value = mock_client
        
        # First payment
        result1 = PaymentService.create_payment(
            user=self.user,
            order_id='ORD-001',
            amount=10000,
            currency='KZT',
            provider='bereke'
        )
        
        # Second identical payment (should be idempotent)
        result2 = PaymentService.create_payment(
            user=self.user,
            order_id='ORD-001',
            amount=10000,
            currency='KZT',
            provider='bereke'
        )
        
        # Both should succeed
        assert result1['success'] is True
        assert result2['success'] is True
        # Same transaction ID
        assert result1['transaction_id'] == result2['transaction_id']


if __name__ == '__main__':
    pytest.main([__file__])
