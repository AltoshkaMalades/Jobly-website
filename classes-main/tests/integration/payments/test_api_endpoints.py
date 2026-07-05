"""
Integration tests for payment API endpoints.
"""
import pytest
import json
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from payments.models import Order, Transaction


@pytest.mark.django_db
class TestPaymentAPI(TestCase):
    """Test payment API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    @patch('payments.services.service.get_payment_client')
    def test_create_payment_endpoint(self, mock_get_client):
        """Test POST /api/payments/create/"""
        mock_client = Mock()
        mock_client.create_payment_request.return_value = {
            'payment_url': 'http://example.com/pay',
            'transaction_id': 'TXN-001',
            'status': 'pending',
            'metadata': {}
        }
        mock_get_client.return_value = mock_client
        
        response = self.client.post(
            '/api/payments/create/',
            data=json.dumps({
                'amount': 10000,
                'currency': 'KZT',
                'description': 'Test payment',
                'provider': 'bereke',
                'return_url': 'http://localhost:8000/return'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'order_id' in data
        assert 'transaction_id' in data
        assert 'payment_url' in data
    
    def test_create_payment_invalid_amount(self):
        """Test payment creation with invalid amount."""
        response = self.client.post(
            '/api/payments/create/',
            data=json.dumps({
                'amount': -100,
                'currency': 'KZT'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_create_payment_unauthenticated(self):
        """Test payment creation requires authentication."""
        client = Client()
        response = client.post(
            '/api/payments/create/',
            data=json.dumps({'amount': 10000}),
            content_type='application/json'
        )
        
        # Should redirect to login
        assert response.status_code in (301, 302, 403)
    
    def test_get_order_status(self):
        """Test GET /api/payments/orders/<order_id>/"""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_order_001',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-002',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='test_txn_001',
            status='pending'
        )
        
        response = self.client.get(f'/api/payments/orders/{order.id}/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['order']['id'] == order.id
        assert data['order']['status'] == 'pending'
        assert len(data['transactions']) == 1
    
    def test_get_order_status_unauthorized(self):
        """Test cannot access other user's order."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        order = Order.objects.create(
            user=other_user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_order_002',
            status='pending'
        )
        
        response = self.client.get(f'/api/payments/orders/{order.id}/')
        
        assert response.status_code == 404
    
    def test_get_transaction_status(self):
        """Test GET /api/payments/transactions/<transaction_id>/"""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_order_003',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-003',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='test_txn_002',
            status='pending'
        )
        
        with patch('payments.services.service.PaymentService.check_transaction_status') as mock_check:
            mock_check.return_value = {
                'success': True,
                'transaction_id': 'TXN-003',
                'status': 'completed',
                'order_status': 'paid'
            }
            
            response = self.client.get(f'/api/payments/transactions/{transaction.transaction_id}/')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['status'] == 'completed'
    
    @patch('payments.services.service.PaymentService.refund_transaction')
    def test_refund_payment_requires_admin(self, mock_refund):
        """Test POST /api/payments/transactions/<transaction_id>/refund requires admin access."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_order_004',
            status='paid'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-004',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='test_txn_003',
            status='completed'
        )
        
        mock_refund.return_value = {
            'success': True,
            'refund_id': 'REFUND-001',
            'amount': 10000
        }
        
        response = self.client.post(
            f'/api/payments/transactions/{transaction.transaction_id}/refund',
            data=json.dumps({'amount': 10000}),
            content_type='application/json'
        )
        
        assert response.status_code == 403
        mock_refund.assert_not_called()

    @patch('payments.services.service.PaymentService.refund_transaction')
    def test_refund_payment_allows_admin(self, mock_refund):
        """Test refunds are allowed for staff users."""
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_order_005',
            status='paid'
        )

        transaction = Transaction.objects.create(
            order=order,
            transaction_id='TXN-005',
            provider='bereke',
            amount=10000,
            currency='KZT',
            idempotency_key='test_txn_004',
            status='completed'
        )

        mock_refund.return_value = {
            'success': True,
            'refund_id': 'REFUND-002',
            'amount': 10000
        }

        response = self.client.post(
            f'/api/payments/transactions/{transaction.transaction_id}/refund',
            data=json.dumps({'amount': 10000}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'refund_id' in data
    
    def test_webhook_bereke_missing_signature(self):
        """Test Bereke webhook with missing signature."""
        response = self.client.post(
            '/api/payments/webhook/bereke',
            data=json.dumps({'transactionId': 'TXN-999'}),
            content_type='application/json'
        )
        
        # Should return 200 regardless
        assert response.status_code == 200
    
    def test_webhook_bereke_invalid_json(self):
        """Test Bereke webhook with invalid JSON."""
        response = self.client.post(
            '/api/payments/webhook/bereke',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_webhook_paypal_valid_event(self):
        """Test PayPal webhook with valid event."""
        order = Order.objects.create(
            user=self.user,
            amount=10000,
            currency='KZT',
            idempotency_key='test_order_005',
            status='pending'
        )
        
        transaction = Transaction.objects.create(
            order=order,
            transaction_id='PAYPAL-001',
            provider='paypal',
            amount=10000,
            currency='KZT',
            idempotency_key='test_txn_004',
            status='pending',
            metadata={'paypal_order_id': 'PAYPAL-ORDER-001'}
        )
        
        response = self.client.post(
            '/api/payments/webhook/paypal',
            data=json.dumps({
                'event_type': 'CHECKOUT.ORDER.COMPLETED',
                'resource': {'id': 'PAYPAL-ORDER-001'}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
