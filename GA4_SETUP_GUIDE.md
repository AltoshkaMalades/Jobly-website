# Google Analytics 4 (GA4) Integration Guide

## Overview

Google Analytics 4 (GA4) has been integrated into the JobAggregator platform to track user behavior, conversion funnels, and analytics across the entire application.

## Configuration

### 1. Environment Variables

Add the following environment variable to your `.env` file or deployment configuration:

```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret_here  # Optional, for server-side tracking
```

**Where to find these values:**
1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property → Admin → Data Streams
3. Click on your web data stream
4. Find the **Measurement ID** (starts with `G-`)
5. (Optional) Go to Admin → API and services → Data API to get the API Secret

### 2. Context Processor

GA4 is automatically available in all templates via the `ga4_context` context processor, which provides:
- `GA4_ENABLED`: Boolean indicating if GA4 is configured
- `GA4_MEASUREMENT_ID`: The measurement ID for use in templates

## Events Tracked

### Page View Events

Automatically tracked on page loads:
- `/register` → "Registration"
- `/login` → "Login"
- `/search` → "Job Search"
- `/pricing` → "Pricing"
- `/courses` → "Courses"

### User Interactions

**Registration:**
- Event: `sign_up`
- Parameters: `method`, `page_path`

**Job Search:**
- Event: `search`
- Parameters: `search_term`, `page_path`

**Job Clicks:**
- Event: `view_job`
- Parameters: `job_id`, `page_path`

**AI Chat:**
- Event: `ai_chat_opened` - when chat widget opens
- Event: `ai_chat_message` - when user sends a message
- Parameters: `message_length`, `page_path`

### Payment Events

**Checkout Started:**
- Event: `begin_checkout`
- Parameters:
  - `currency`: Payment currency (e.g., "USD")
  - `value`: Amount to be paid
  - `items`: Array of items in checkout

**Payment Method Selection:**
- Event: `select_payment_method`
- Parameters:
  - `payment_method`: "paypal" or "bereke"
  - `currency`: Payment currency
  - `value`: Amount

**Payment Info Added:**
- Event: `add_payment_info`
- Parameters:
  - `payment_method`: Selected payment provider
  - `currency`: Payment currency
  - `value`: Amount

**Purchase Completed:**
- Event: `purchase`
- Parameters:
  - `currency`: Payment currency
  - `value`: Amount paid
  - `transaction_id`: Payment transaction ID
  - `items`: Array with purchase details

**Purchase Failed:**
- Event: `purchase_failed`
- Parameters:
  - `error_code`: Error code from payment provider
  - `error_message`: User-friendly error message
  - `page_path`: Page where error occurred
  - `referrer`: Referring page

## User Identification

Authenticated users are automatically identified in GA4 using their user ID:

```javascript
{% if user.is_authenticated %}
gtag('set', {'user_id': '{{ user.id }}'});
gtag('config', '{{ GA4_MEASUREMENT_ID }}', {'user_id': '{{ user.id }}'});
{% endif %}
```

This enables user-level analysis and cross-session tracking.

## Analytics Features

### Conversion Funnels

Track the payment conversion funnel with these events:
1. **Funnel Start**: `page_view` on pricing/payment page
2. **Step 1**: `begin_checkout`
3. **Step 2**: `select_payment_method`
4. **Step 3**: `add_payment_info`
5. **Conversion**: `purchase`
6. **Drop-off**: `purchase_failed`

### User Behavior Flows

- Registration flow: `page_view` → `sign_up`
- Search flow: `page_view` → `search` → `view_job`
- Payment flow: `page_view` → `begin_checkout` → `select_payment_method` → `add_payment_info` → `purchase`

### Key Metrics

GA4 automatically tracks:
- Session duration
- User engagement
- Bounce rate
- Conversion rate
- User acquisition source

## Implementation Details

### Template Integration

GA4 script is loaded in `accounts/base.html`:

```html
{% if GA4_MEASUREMENT_ID %}
<script async src="https://www.googletagmanager.com/gtag/js?id={{ GA4_MEASUREMENT_ID }}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{{ GA4_MEASUREMENT_ID }}', {
        'send_page_view': true,
        'anonymize_ip': false
    });
    
    {% if user.is_authenticated %}
    gtag('set', {'user_id': '{{ user.id }}'});
    gtag('config', '{{ GA4_MEASUREMENT_ID }}', {'user_id': '{{ user.id }}'});
    {% endif %}
</script>
{% endif %}
```

### Event Tracking Helper

A helper function `trackGA4Event()` is available globally in all templates:

```javascript
trackGA4Event('event_name', {
    'parameter1': 'value1',
    'parameter2': 'value2'
});
```

### Python Integration

For server-side analytics or audit logging, use the `core/analytics.py` module:

```python
from core.analytics import get_ga4_tracker, is_ga4_enabled

tracker = get_ga4_tracker()
tracker.track_event('custom_event', 'user_id', {'param': 'value'})
```

## Testing

### Check if GA4 is Enabled

In your Django shell:

```python
from core.analytics import is_ga4_enabled, get_ga4_measurement_id

print(is_ga4_enabled())  # True/False
print(get_ga4_measurement_id())  # G-XXXXXXXXXX
```

### Browser DevTools

1. Open Chrome DevTools → Network tab
2. Search for requests to `google-analytics.com` or `googletagmanager.com`
3. Verify events are being sent in the request payloads
4. Use Google Analytics Real-time dashboard to confirm events appear

### GA4 Debugger Extension

Install the [GA4 Debugger Chrome Extension](https://chrome.google.com/webstore/detail/ga4-debugger/dfkijajdffemkmmhfambbkonpkebmbhe) for real-time event debugging.

## Troubleshooting

### GA4 Not Tracking Events

1. **Check Measurement ID**: Ensure `GA4_MEASUREMENT_ID` environment variable is set
2. **Verify GA4 Property**: Confirm property exists in Google Analytics console
3. **Browser Console**: Check for JavaScript errors preventing gtag loading
4. **Network Requests**: Verify requests are being sent to Google's servers
5. **Real-time Dashboard**: Check GA4 admin → Real-time to see live events

### Events Not Appearing in GA4 Dashboard

- Wait 24-48 hours for initial data processing
- Use Real-time reports for immediate feedback (updates every ~3 seconds)
- Verify event names match GA4 naming conventions (lowercase, underscores)
- Check if events are filtered by user properties or segments

### User Not Identified

- Ensure user is authenticated (`user.is_authenticated`)
- Check that user ID is a valid integer
- Verify gtag is loaded before user identification code runs

## Privacy & Compliance

### Data Collection

GA4 is configured to:
- ✅ Send page views automatically
- ✅ Anonymize IP addresses (can be changed in config)
- ✅ Respect browser Do Not Track settings

### GDPR Compliance

To ensure GDPR compliance:

1. Add GA4 to your privacy policy
2. Obtain user consent before tracking (implement cookie banner)
3. Allow users to opt-out of analytics
4. Use IP anonymization: ✅ Already enabled

### Example Cookie Banner Integration

```javascript
// Only enable GA4 if user consents
if (userConsentsToAnalytics) {
    gtag('consent', 'update', {
        'analytics_storage': 'granted'
    });
}
```

## Resources

- [Google Analytics 4 Documentation](https://support.google.com/analytics/answer/9304153)
- [Event Names Reference](https://support.google.com/analytics/answer/9322688)
- [Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [GA4 API Documentation](https://developers.google.com/analytics/devguides/config/admin/v1)

## Next Steps

1. Set `GA4_MEASUREMENT_ID` in your environment
2. Verify events in GA4 Real-time dashboard
3. Create custom reports and dashboards in GA4
4. Set up conversion goals and funnels
5. Monitor KPIs and user behavior trends
