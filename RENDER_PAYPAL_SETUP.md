# 🚀 PayPal Setup for Render Hosting

## ⚠️ Current Issue on Render

**Error:** "Ошибка платежа" (Payment Error) when processing PayPal payment

**Root Cause:** Environment variables likely not configured in Render dashboard

---

## ✅ Step 1: Set Environment Variables on Render

### In Render Dashboard:
1. Go to: **Dashboard → Your Project → Settings → Environment**
2. Add these variables:

```
PAYPAL_SANDBOX=true
PAYPAL_CLIENT_ID=ASncwfh4LP_gudXxInl8LvRNlUTfA6kC8zkdVP-rpxR7wJ67rXpTuxjK4sH7WE0vS8wR94LBfvaYSdxO
PAYPAL_CLIENT_SECRET=EN4ep5jW2HREPdMJGk31GNI1yzCjpqziHyu_G_soRsAl-u2K06hM00RCYqjin87nC9n1cmDqNq-2zB87
PAYPAL_WEBHOOK_ID=(leave empty for now - we'll add after testing)
```

3. **Deploy** → New deployment will use these variables

---

## ✅ Step 2: Verify Environment Variables Are Set

After deployment, check if variables are loaded:

**Method 1: Check Render Logs**
- Go to: Dashboard → Your Project → Logs
- Search for: `PayPal credentials`
- Should NOT see: `"using mock mode"` warning

**Method 2: Create Test Endpoint (Optional)**

Add this to `payments/views.py`:

```python
from django.http import JsonResponse

@csrf_exempt
def debug_paypal_config(request):
    """Debug endpoint to verify PayPal config"""
    import os
    return JsonResponse({
        'PAYPAL_SANDBOX': os.getenv('PAYPAL_SANDBOX', 'NOT SET'),
        'PAYPAL_CLIENT_ID': 'CONFIGURED' if os.getenv('PAYPAL_CLIENT_ID') else 'NOT SET',
        'PAYPAL_CLIENT_SECRET': 'CONFIGURED' if os.getenv('PAYPAL_CLIENT_SECRET') else 'NOT SET',
        'DEBUG': DEBUG
    })
```

Add to `core/urls.py`:
```python
path('debug/paypal/', views.debug_paypal_config, name='debug_paypal_config'),
```

Then visit: `https://your-render-url/debug/paypal/`

---

## ✅ Step 3: Configure PayPal Webhook (Important!)

Your Render URL will be something like: `https://jobaggregatoryour-uuid.onrender.com`

**In PayPal Sandbox Dashboard:**

1. Go to: **Developer → Accounts → Sandbox → Business Account**
2. Click on **Apps & Credentials** tab
3. Click your app name (or create one if needed)
4. Scroll down to **Webhook Configuration** or **Webhooks**
5. Add this webhook URL:

```
https://your-render-url/api/payments/webhook/paypal/
```

**Select these events:**
- `CHECKOUT.ORDER.CREATED`
- `CHECKOUT.ORDER.APPROVED` 
- `CHECKOUT.ORDER.COMPLETED`
- `PAYMENT.CAPTURE.COMPLETED`
- `PAYMENT.CAPTURE.DENIED`

6. Save the **Webhook ID** and add to Render environment:
   ```
   PAYPAL_WEBHOOK_ID=WH_XXXXX...
   ```

---

## ✅ Step 4: Test Locally First

Before going to Render, ensure it works locally:

```bash
# In classes-main/
python manage.py runserver 8000
```

Visit: `http://localhost:8000/accounts/pricing/`
- Click a payment button
- Complete PayPal checkout in sandbox
- Should see success page with order details

**If it fails locally:** The issue is NOT hosting-related. Check:
- Django settings loaded correctly
- Database migrations run
- Static files collected

---

## ✅ Step 5: Common Render Issues & Solutions

### Issue: "PayPal credentials not configured"

**Solution:**
```bash
# In Render build script, add:
python manage.py collectstatic --noinput
python manage.py migrate
```

Make sure environment variables are set BEFORE deployment.

### Issue: "Invalid credentials - unauthorized"

**Solution:**
- Verify PAYPAL_CLIENT_ID is correct (no extra spaces)
- Verify PAYPAL_CLIENT_SECRET is correct
- Make sure PAYPAL_SANDBOX=true (using sandbox credentials with production API)

### Issue: "Webhook validation failed"

**Solution:**
- Check PAYPAL_WEBHOOK_ID is set in environment
- Verify webhook URL is reachable from PayPal
- Check Render logs for incoming webhook requests:
  ```bash
  # In Render logs, search for:
  webhook
  paypal
  ```

### Issue: "CORS error" or "CSP blocking PayPal"

**Already Fixed!** Check that CSP is applied:
- Go to: `core/middleware.py`
- Should include: `https://www.paypal.com` in script-src
- Should include: `https://sandbox.paypal.com` in frame-src

---

## 📋 Render Deployment Checklist

- [ ] Environment variables set in Render dashboard
- [ ] PAYPAL_CLIENT_ID & PAYPAL_CLIENT_SECRET copied exactly
- [ ] PAYPAL_SANDBOX=true (for sandbox credentials)
- [ ] Database migrated on first deployment
- [ ] Static files collected
- [ ] CSP middleware has PayPal domains (core/middleware.py)
- [ ] Webhook URL configured in PayPal dashboard
- [ ] PAYPAL_WEBHOOK_ID set in Render environment
- [ ] Payment page loads without errors
- [ ] PayPal button renders correctly
- [ ] Test payment in sandbox mode

---

## 🔗 PayPal App Setup (If Not Done Yet)

If PayPal app doesn't exist:

1. Go to: https://developer.paypal.com/dashboard
2. Sign in with your PayPal account
3. **Apps & Credentials** → **Create App**
4. Choose **Merchant** app type
5. Copy **Client ID** and **Secret**
6. Use these in PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET

---

## 🧪 Test Payment Flow

**After setup is complete:**

1. Visit your Render URL
2. Go to: `/accounts/pricing/`
3. Click payment button (e.g., Professional $9.99/month)
4. Login if needed
5. Click PayPal button
6. You'll be redirected to PayPal sandbox
7. Use sandbox test account to complete payment
8. Should be redirected to success page with order details

**PayPal Sandbox Test Accounts:**
- **Buyer**: sb-XXXXXXXXX@personal.example.com (password: any)
- **Seller**: your PayPal account

---

## 📊 Monitoring on Render

**View Logs:**
```bash
# In Render dashboard → Logs
# Search for these patterns:
"PayPal" - shows all PayPal activity
"error" - shows all errors
"webhook" - shows webhook activity
```

**Example of successful payment log:**
```
[2026-06-18] Order created: ORD-123-ABC12345 for user:testpayment
[2026-06-18] PayPal API response: 201 Created
[2026-06-18] Webhook received: CHECKOUT.ORDER.COMPLETED
[2026-06-18] Payment captured: $9.99 USD
```

**Example of failed payment log:**
```
[2026-06-18] PayPal credentials not configured - using mock mode
[2026-06-18] API error: INVALID_REQUEST
[2026-06-18] Payment failed for user:testpayment
```

---

## 🚀 Production Deployment (Later)

When ready for production:

1. Create PayPal Live App (not Sandbox)
2. Get Live Client ID & Secret
3. On Render, change environment:
   ```
   PAYPAL_SANDBOX=false
   PAYPAL_CLIENT_ID=<LIVE_CLIENT_ID>
   PAYPAL_CLIENT_SECRET=<LIVE_CLIENT_SECRET>
   ```
4. Update CSP to allow production PayPal:
   ```python
   # core/middleware.py - update for production
   'script-src': ... https://www.paypal.com ...
   'frame-src': ... https://www.paypal.com ...
   ```

---

## ✅ Summary

- ✓ Set environment variables on Render
- ✓ Test locally first
- ✓ Configure webhook in PayPal dashboard
- ✓ Deploy with updated env vars
- ✓ Monitor logs for errors
- ✓ Test payment flow end-to-end
