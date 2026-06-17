# 💳 Payment Integration Guide

This guide covers the payment system implementation including Bereke Bank and PayPal integrations, webhooks, order state management, and analytics tracking.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Payment Providers](#payment-providers)
3. [Local Development Setup](#local-development-setup)
4. [API Endpoints](#api-endpoints)
5. [Webhook Configuration](#webhook-configuration)
6. [State Machine](#state-machine)
7. [Idempotency & Duplicate Detection](#idempotency--duplicate-detection)
8. [Testing](#testing)
9. [Environment Variables](#environment-variables)

---

## 🏗️ Architecture Overview

The payment system follows a clean, provider-agnostic architecture:

### Components

- **Payment Models** (`payments/models.py`):
  - `Order`: Represents a purchase order with state machine
  - `Transaction`: Records payment transactions with provider details
  - `StateTransitionLog`: Audit trail of order status changes

- **Payment Clients** (`payments/services/`):
  - `PaymentClient` (ABC): Abstract base for all providers
  - `BereкeBankClient`: Bereke Bank Sandbox integration
  - `PayPalClient`: PayPal Orders API v2 integration

- **Payment Service** (`payments/services/service.py`):
  - `PaymentService`: Business logic orchestrator
  - Provider abstraction and switching
  - Idempotency key management
  - PostHog event tracking

- **API Endpoints** (`payments/views.py`):
  - Payment creation
  - Status checking (polling)
  - Refunds
  - Webhook handlers (Bereke, PayPal)

- **Analytics** (`core/posthog.py`):
  - PostHog SDK integration
  - User identification
  - Business event tracking

---

## 💰 Payment Providers

### Bereke Bank Sandbox

**Status**: Mock mode by default (no credentials needed for development)

**Features**:
- Payment request creation
- Transaction status checking
- Refunds (full and partial)
- HMAC-SHA256 webhook signature validation

**Credentials** (from environment):
```
BEREKE_SANDBOX=true
BEREKE_API_KEY=your-api-key
BEREKE_API_SECRET=your-webhook-secret
BEREKE_MERCHANT_ID=MERCHANT_001
```

**Mock Mode**: Returns realistic responses without actual API calls. Useful for:
- Development without credentials
- Testing payment flows
- Demo purposes

### PayPal Sandbox

**Status**: Mock mode by default

**Features**:
- Order creation using PayPal Orders API v2
- Capture/refund operations
- Webhook event handling
- Full/partial refunds

**Credentials** (from environment):
```
PAYPAL_SANDBOX=true
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_WEBHOOK_ID=your-webhook-id
```

**Mock Mode**: Same as Bereke - realistic responses without API calls

---

## 🔧 Local Development Setup

### 1. Install PostHog SDK

```bash
pip install posthog==3.0.2
```

### 2. Configure Environment Variables

Copy and fill `.env.example` → `.env`:

```bash
# PostHog (optional for development)
POSTHOG_API_KEY=your-key
POSTHOG_API_URL=https://app.posthog.com

# Bereke Bank (optional - uses mock mode without credentials)
BEREKE_SANDBOX=true
BEREKE_API_KEY=your-key-here
BEREKE_API_SECRET=your-secret-here

# PayPal (optional - uses mock mode without credentials)
PAYPAL_SANDBOX=true
PAYPAL_CLIENT_ID=your-client-id-here
PAYPAL_CLIENT_SECRET=your-client-secret-here

# Webhook (for ngrok/local testing)
WEBHOOK_BASE_URL=http://localhost:8000
```

### 3. Run Migrations

```bash
python manage.py makemigrations payments
python manage.py migrate
```

### 4. Access Admin Panel

```bash
python manage.py createsuperuser
python manage.py runserver
# Visit: http://localhost:8000/admin/
```

---

## 🔌 API Endpoints

### 1. Create Payment

**Endpoint**: `POST /api/payments/create/`

**Authentication**: Required (login_required)

**Request**:
```json
{
  "amount": 10000,                    // Minor units (cents/tiyn)
  "currency": "KZT",                  // ISO 4217 code
  "description": "Order #123",
  "provider": "bereke",               // or "paypal"
  "return_url": "https://example.com/return"
}
```

**Response** (Success):
```json
{
  "success": true,
  "order_id": 42,
  "transaction_id": "BEREKE-a1b2c3d4e5f6",
  "payment_url": "https://sandbox.berekebank.kz/pay/BEREKE-a1b2c3d4e5f6"
}
```

**Response** (Error):
```json
{
  "success": false,
  "error": "Amount must be positive"
}
```

**Example CURL**:
```bash
curl -X POST http://localhost:8000/api/payments/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "amount": 50000,
    "currency": "KZT",
    "description": "Premium subscription",
    "provider": "bereke",
    "return_url": "http://localhost:3000/success"
  }'
```

---

### 2. Get Order Status

**Endpoint**: `GET /api/payments/orders/<order_id>/`

**Response**:
```json
{
  "success": true,
  "order": {
    "id": 42,
    "status": "paid",
    "amount": 50000,
    "currency": "KZT",
    "created_at": "2026-06-16T10:30:00Z"
  },
  "transactions": [
    {
      "transaction_id": "BEREKE-a1b2c3d4e5f6",
      "provider": "bereke",
      "status": "completed",
      "completed_at": "2026-06-16T10:32:00Z"
    }
  ]
}
```

**Example CURL**:
```bash
curl -X GET http://localhost:8000/api/payments/orders/42/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Check Transaction Status

**Endpoint**: `GET /api/payments/transactions/<transaction_id>/`

**Response**:
```json
{
  "success": true,
  "transaction_id": "BEREKE-a1b2c3d4e5f6",
  "status": "completed",
  "order_status": "paid"
}
```

**Example CURL**:
```bash
curl -X GET http://localhost:8000/api/payments/transactions/BEREKE-a1b2c3d4e5f6/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Refund Transaction

**Endpoint**: `POST /api/payments/transactions/<transaction_id>/refund`

**Request** (optional amount):
```json
{
  "amount": 25000  // Partial refund (if omitted, full refund)
}
```

**Response**:
```json
{
  "success": true,
  "refund_id": "REFUND-abcdef123456",
  "amount": 25000
}
```

**Example CURL**:
```bash
curl -X POST http://localhost:8000/api/payments/transactions/BEREKE-a1b2c3d4e5f6/refund \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount": 25000}'
```

---

## 🪝 Webhook Configuration

### Local Testing with ngrok

Webhooks require a public URL. Use ngrok for local development:

#### Step 1: Install ngrok

```bash
# macOS
brew install ngrok

# Windows (via Chocolatey)
choco install ngrok

# Or download from https://ngrok.com/download
```

#### Step 2: Start ngrok

```bash
ngrok http 8000
```

Output:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```

#### Step 3: Configure Environment

```bash
WEBHOOK_BASE_URL=https://abc123.ngrok.io
```

#### Step 4: Register Webhooks with Provider

For **Bereke Bank**:
```
Webhook URL: https://abc123.ngrok.io/api/payments/webhook/bereke
Signature header: X-Bereke-Signature
```

For **PayPal**:
```
Webhook URL: https://abc123.ngrok.io/api/payments/webhook/paypal
Event types: CHECKOUT.ORDER.COMPLETED, CHECKOUT.ORDER.APPROVED
```

---

### Webhook Endpoints

#### Bereke Webhook

**Endpoint**: `POST /api/payments/webhook/bereke`

**Headers**:
```
X-Bereke-Signature: hmac-sha256-signature
Content-Type: application/json
```

**Payload**:
```json
{
  "transactionId": "BEREKE-a1b2c3d4e5f6",
  "status": "PAID",          // or "FAILED", "REFUNDED"
  "orderId": "ORD-123",
  "amount": 50000,
  "currency": "KZT",
  "timestamp": "2026-06-16T10:32:00Z"
}
```

#### PayPal Webhook

**Endpoint**: `POST /api/payments/webhook/paypal`

**Headers**:
```
PayPal-Transmission-Sig: signature
Content-Type: application/json
```

**Payload**:
```json
{
  "event_type": "CHECKOUT.ORDER.COMPLETED",
  "resource": {
    "id": "PAYPAL-ORDER-ID",
    "status": "COMPLETED"
  }
}
```

---

## 🔄 State Machine

Order status transitions follow a defined state machine:

```
Created
  ↓
Pending → Failed
  ↓
Paid → Refunded
  ↓
Fulfilled
  ↓
Completed
```

### Valid Transitions

| From Status | Valid Targets |
|------------|---------------|
| created | pending, failed |
| pending | paid, failed |
| paid | fulfilled, refunded |
| fulfilled | completed |
| completed | ❌ (terminal) |
| failed | ❌ (terminal) |
| refunded | ❌ (terminal) |

### Transition Examples

```python
from payments.models import Order

order = Order.objects.get(id=42)

# Valid transition
order.transition_to('pending', actor='user_123')

# Invalid transition (raises ValidationError)
try:
    order.transition_to('completed')  # Can't skip 'paid' and 'fulfilled'
except ValidationError as e:
    print(f"Invalid transition: {e}")

# Check if transition is allowed before attempting
if order.can_transition_to('paid'):
    order.transition_to('paid', actor='webhook')
```

### Audit Trail

All transitions are logged:

```python
from payments.models import StateTransitionLog

logs = StateTransitionLog.objects.filter(order=order)
for log in logs:
    print(f"{log.from_status} → {log.to_status} | Actor: {log.actor} | {log.timestamp}")
```

---

## 🔐 Idempotency & Duplicate Detection

Duplicate payments are automatically prevented using idempotency keys.

### How It Works

1. **Key Generation**: `hash(user_id + order_id + amount)`
2. **Check**: Before creating payment, system checks if key exists
3. **Return**: If duplicate found, return existing transaction (HTTP 200)
4. **Database**: Unique constraint on `idempotency_key` field

### Example Flow

```python
# First request (creates transaction)
result1 = PaymentService.create_payment(
    user=user,
    order_id='ORD-001',
    amount=50000,
    provider='bereke'
)
# result1['transaction_id'] = 'BEREKE-abc123'
# result1['message'] = 'Payment created'

# Duplicate request (within seconds, network retry)
result2 = PaymentService.create_payment(
    user=user,
    order_id='ORD-001',
    amount=50000,
    provider='bereke'
)
# result2['transaction_id'] = 'BEREKE-abc123'  ← Same!
# result2['message'] = 'Payment already created'
# result2['success'] = True  ← Still succeeds (idempotent)
```

### Implementation Details

- **Idempotency Key**: Stored in both `Order` and `Transaction` models
- **Uniqueness**: Database constraint prevents duplicate entries
- **Deterministic**: Same inputs always generate same key
- **Safe**: No additional charges on duplicate attempts

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/unit/payments/ -v          # Unit tests
pytest tests/integration/payments/ -v   # Integration tests
pytest tests/*/payments/ -v --cov       # With coverage
```

### Unit Tests

**File**: `tests/unit/payments/test_models_and_services.py`

Tests cover:
- Order state machine (valid/invalid transitions)
- Transaction creation and idempotency
- Bereke Bank client (mock mode)
- PayPal client (mock mode)
- Payment service (creation, duplication, status checking)

```bash
pytest tests/unit/payments/test_models_and_services.py -v
```

### Integration Tests

**File**: `tests/integration/payments/test_api_endpoints.py`

Tests cover:
- Payment creation endpoint
- Order status retrieval
- Transaction status polling
- Refund endpoint
- Webhook handling (Bereke & PayPal)
- Authorization checks
- Error handling

```bash
pytest tests/integration/payments/test_api_endpoints.py -v
```

### Test Happy Path

```bash
# 1. Create payment
curl -X POST http://localhost:8000/api/payments/create/ \
  -d '{"amount": 10000, "currency": "KZT", "provider": "bereke"}'

# 2. Check order status
curl http://localhost:8000/api/payments/orders/<order_id>/

# 3. Check transaction status
curl http://localhost:8000/api/payments/transactions/<transaction_id>/

# 4. Refund
curl -X POST http://localhost:8000/api/payments/transactions/<transaction_id>/refund \
  -d '{"amount": 10000}'
```

---

## 📊 Analytics Events

### PostHog Integration

All payment events are automatically tracked:

| Event | Properties | Use Case |
|-------|-----------|----------|
| `checkout_started` | user_id, order_id, amount, provider | Acquisition funnel |
| `payment_completed` | user_id, order_id, amount, provider | Revenue tracking |
| `payment_failed` | user_id, order_id, amount, provider, error | Funnel drop-off |
| `payment_duplicated` | user_id, amount, provider | Duplicate detection |
| `refund_initiated` | user_id, order_id, refund_amount, provider | Churn analysis |

### Event Flow

```
User Visits → Checkout Started
           ↓
         Payment Processing
           ↓
      ┌────┴────┐
      ↓         ↓
  Completed   Failed
      ↓         ↓
   Refund?   Retry?
```

### Viewing Events in PostHog

1. Log in to PostHog
2. Go to Events
3. Filter by event name (e.g., `payment_completed`)
4. View user properties, timestamps, properties

---

## 🌐 Environment Variables

### Required for Production

```bash
# Bereke Bank
BEREKE_API_KEY=your-actual-api-key
BEREKE_API_SECRET=your-webhook-secret
BEREKE_MERCHANT_ID=YOUR_MERCHANT_ID

# PayPal
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_WEBHOOK_ID=your-webhook-id

# PostHog
POSTHOG_API_KEY=your-posthog-key
```

### Optional for Development

```bash
BEREKE_SANDBOX=true      # Use sandbox API
PAYPAL_SANDBOX=true      # Use sandbox API
DEBUG=False              # Disable debug mode
```

---

## 🚀 Deployment Checklist

- [ ] Set all credentials in production environment
- [ ] Run migrations: `python manage.py migrate`
- [ ] Register webhook URLs with payment providers
- [ ] Test webhook delivery with provider sandboxes
- [ ] Set up PostHog analytics dashboard
- [ ] Configure error alerting (New Relic, Sentry)
- [ ] Test refund workflow
- [ ] Verify SSL certificates (HTTPS everywhere)
- [ ] Load test payment endpoints
- [ ] Set up audit logging
- [ ] Document support procedures

---

## 📚 Additional Resources

- [Bereke Bank API Docs](https://berekebank.kz/api-docs)
- [PayPal Orders API v2](https://developer.paypal.com/docs/api/orders/v2/)
- [PostHog Documentation](https://posthog.com/docs)
- [Django Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/)

---

## 🆘 Troubleshooting

### "Transaction not found"
- Check transaction_id spelling
- Verify user has access to order
- Check database for Transaction record

### "Invalid state transition"
- Review VALID_STATE_TRANSITIONS in models.py
- Check order.status before transition
- Call order.can_transition_to() first

### Webhook not triggering
- Verify ngrok is running: `ngrok http 8000`
- Check webhook URL is registered with provider
- Verify webhook secret matches WEBHOOK_SECRET
- Check Django logs for errors

### PostHog events not showing
- Verify POSTHOG_API_KEY is set
- Check PostHog SDK is installed: `pip list | grep posthog`
- Enable DEBUG=True to see SDK logs
- Verify API key is correct in PostHog dashboard
