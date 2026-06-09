# Google OAuth & reCAPTCHA Setup Guide

## Overview

This guide explains how to set up Google OAuth and reCAPTCHA for production deployment on Render.com.

## Prerequisites

You'll need:
1. Google Console project with OAuth 2.0 credentials
2. reCAPTCHA v3 site keys from Google
3. Environment variables configured in Render dashboard

## Step 1: Get Google OAuth Credentials

### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "jobly")
3. Go to **APIs & Services** → **OAuth consent screen**
4. Set up OAuth consent screen (external, then add scopes)
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **OAuth client ID** → **Web application**
7. Add authorized redirect URIs:
   - `https://jobly.kz/accounts/google/login/callback/` (production)
   - `http://localhost:8000/accounts/google/login/callback/` (local dev)
8. Copy the **Client ID** and **Client Secret**

## Step 2: Get reCAPTCHA v3 Keys

1. Go to [Google reCAPTCHA Console](https://www.google.com/recaptcha/admin)
2. Click **Create or select** to create a new site
3. Configure as:
   - **Label:** jobly
   - **reCAPTCHA version:** reCAPTCHA v3
   - **Domains:** `jobly.kz`, `*.render.com` (or your Render domain)
4. Copy the **Site Key** and **Secret Key**

## Step 3: Set Environment Variables on Render

In your Render service environment variables, set:

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id-from-google-cloud
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-from-google-cloud
SITE_DOMAIN=jobly.kz

# reCAPTCHA v3
RECAPTCHA_PUBLIC_KEY=your-site-key-from-recaptcha
RECAPTCHA_PRIVATE_KEY=your-secret-key-from-recaptcha

# Optional: For production
DEBUG=False
ALLOWED_HOSTS=jobly.kz,www.jobly.kz
```

## Step 4: Database Setup

The Docker deployment automatically:
1. Runs migrations: `python manage.py migrate`
2. Cleans duplicate OAuth apps: `python manage.py cleanup_socialapps`
3. Sets up Google OAuth: `python manage.py setup_google_oauth`

This means everything is configured automatically during deployment!

## Step 5: Verify Setup

After deployment, check:

### Check 1: Admin Panel
1. Go to `https://jobly.kz/admin/`
2. Navigate to **Sites** → Make sure domain is set to `jobly.kz`
3. Navigate to **Social applications**
   - Should see one Google app
   - Verify Client ID and Secret are set
   - Verify it's connected to your Site

### Check 2: reCAPTCHA
1. Go to `https://jobly.kz/register/`
2. You should see a reCAPTCHA badge in bottom-right corner
3. Fill form and submit - reCAPTCHA should validate automatically

### Check 3: Google Login
1. Go to `https://jobly.kz/login/` or `/register/`
2. You should see "Continue with Google" button
3. Click it - should redirect to Google login
4. After auth - should create user account

## Manual Commands (if needed)

### Clean duplicate OAuth apps:
```bash
python manage.py cleanup_socialapps
```

### Manually setup Google OAuth:
```bash
python manage.py setup_google_oauth \
  --client-id YOUR_CLIENT_ID \
  --secret YOUR_CLIENT_SECRET \
  --domain jobly.kz
```

Or use environment variables (preferred):
```bash
GOOGLE_OAUTH_CLIENT_ID=YOUR_ID GOOGLE_OAUTH_CLIENT_SECRET=YOUR_SECRET python manage.py setup_google_oauth
```

### Update Site domain:
```bash
python manage.py shell
>>> from django.contrib.sites.models import Site
>>> s = Site.objects.get(id=1)
>>> s.domain = 'jobly.kz'
>>> s.save()
```

## Troubleshooting

### "TemplateDoesNotExist: django_recaptcha/widget_v3.html"
- Ensure `django_recaptcha` is in INSTALLED_APPS ✓ (already done)
- Ensure package is installed: `pip install django-recaptcha==4.0.0` ✓

### "MultipleObjectsReturned" on login/register
- Run: `python manage.py cleanup_socialapps`
- This removes duplicate Google OAuth apps

### Google login shows "Connection refused"
- Check Google OAuth credentials are correct
- Check redirect URI is registered in Google Console
- Verify SITE_DOMAIN environment variable matches domain

### reCAPTCHA not validating
- Check RECAPTCHA_PUBLIC_KEY and RECAPTCHA_PRIVATE_KEY are set
- Verify domain is added to reCAPTCHA console
- Check score threshold in form (currently 0.5)

## Testing Locally

1. Set test keys in `.env`:
   ```bash
   RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
   RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
   ```

2. For Google OAuth testing locally:
   - Set in Google Console: `http://localhost:8000/accounts/google/login/callback/`
   - Run management command with test credentials
   - Or use: `python manage.py setup_google_oauth --client-id TEST_ID --secret TEST_SECRET --domain localhost:8000`

## Security Notes

⚠️ **Never commit credentials to Git!**
- Always use environment variables (already configured via Render secrets)
- Production and development use different credentials
- Test keys for reCAPTCHA don't enforce scoring in production

✅ **Current setup:**
- Uses test keys for reCAPTCHA (override in production via env vars)
- Credentials loaded from environment (secure)
- Fallback templates for when packages not installed (safe)
- Duplicate app cleanup on deploy (prevents MultipleObjectsReturned errors)
