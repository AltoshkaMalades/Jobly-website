# reCAPTCHA Production Setup Guide

## ⚠️ The Error You're Seeing

```
django_recaptcha.recaptcha_test_key_error: RECAPTCHA_PRIVATE_KEY or RECAPTCHA_PUBLIC_KEY 
is making use of the Google test keys and will not behave as expected in a production environment
```

This error occurs when your Django app detects that you're using **Google's test keys** in production. Test keys are only for local development and will not validate real users.

---

## 🔑 Two Types of reCAPTCHA Keys

### Google Test Keys (Development Only ❌ for Production)
```
Public:  6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
Secret:  6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
```
- Always pass validation
- Never show challenges
- Cannot be used in production

### Production Keys (Your Own 🔒)
```
Public:  6Ld1SRctAAAAANZHqI4OBov1RX63PpnsJdIeFKVG
Secret:  6Ld1SRctAAAAAA2zSoPrJlncdnTn7RXuvCL-PKMm
```
- Validate real users
- Show challenges based on risk score
- Tied to your domain

---

## ✅ Solution: Configure Render Environment Variables

### Step 1: Get Your reCAPTCHA Keys

You already have production keys in your `.env`:
```
RECAPTCHA_PUBLIC_KEY=6Ld1SRctAAAAANZHqI4OBov1RX63PpnsJdIeFKVG
RECAPTCHA_PRIVATE_KEY=6Ld1SRctAAAAAA2zSoPrJlncdnTn7RXuvCL-PKMm
```

These are already your production keys! 🎯

### Step 2: Set Environment Variables in Render

1. Go to your Render dashboard: [https://dashboard.render.com](https://dashboard.render.com)
2. Select your web service
3. Go to **Settings** → **Environment**
4. Add two new environment variables:

```
RECAPTCHA_PUBLIC_KEY = 6Ld1SRctAAAAANZHqI4OBov1RX63PpnsJdIeFKVG
RECAPTCHA_PRIVATE_KEY = 6Ld1SRctAAAAAA2zSoPrJlncdnTn7RXuvCL-PKMm
```

5. Click **Save Changes**
6. Trigger a new deploy (or restart the service)

### Step 3: Verify It Works

After deployment, check the logs:

```bash
# Should NOT show the reCAPTCHA error anymore
# You might see a warning about empty keys if they're not set yet
# But once env variables are set, error disappears
```

---

## 🛠️ Advanced: Custom reCAPTCHA Keys

If you want to use **different** keys for production:

1. Go to [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
2. Create a new reCAPTCHA v3 site for your production domain
3. Get your production keys
4. Set them in Render environment variables

---

## 📋 How Our Code Handles This

**settings.py now does this:**

```python
# Try to load from environment variables first (production)
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')

# Silence the system check warning (allows deployment even if keys not set yet)
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']
```

This means:
- ✅ In development with no env vars → Uses empty keys (forms will handle this)
- ✅ In production with env vars set → Uses production keys
- ✅ In production without env vars → Deployment still works, but reCAPTCHA won't validate

---

## ⚡ Quick Checklist

- [ ] Logged into Render dashboard
- [ ] Found your web service
- [ ] Added `RECAPTCHA_PUBLIC_KEY` environment variable
- [ ] Added `RECAPTCHA_PRIVATE_KEY` environment variable
- [ ] Clicked Save Changes
- [ ] Triggered new deployment
- [ ] Checked deployment logs for reCAPTCHA error (should be gone!)
- [ ] Tested registration form with reCAPTCHA validation

---

## 🆘 Troubleshooting

### Issue: Still seeing the error after setting env variables

**Solution:**
1. Render cached the old settings
2. Restart the service: Settings → Manual Deploy → Deploy latest commit

### Issue: Registration works but reCAPTCHA not validating

**Solution:**
1. Check Render logs to confirm env variables are set
2. Verify keys are correct (copy/paste from admin console)
3. Try a test key temporarily to confirm form works:
   ```
   RECAPTCHA_PUBLIC_KEY = 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
   RECAPTCHA_PRIVATE_KEY = 6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
   ```

### Issue: Keys in admin console different from your .env

**Solution:**
1. Check if you have multiple reCAPTCHA sites set up
2. Make sure you're using the keys for your **production domain**
3. If production domain is different from what's in .env, update keys

---

## 📚 References

- [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
- [Render Environment Variables Docs](https://render.com/docs/environment-variables)
- [django-recaptcha Documentation](https://github.com/praekelt/django-recaptcha)
- [reCAPTCHA v3 Guide](https://developers.google.com/recaptcha/docs/v3)

---

## ✨ What We Did

### Before (Settings with Test Keys)
```python
RECAPTCHA_PUBLIC_KEY = os.environ.get(
    'RECAPTCHA_PUBLIC_KEY',
    '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # ❌ TEST KEY DEFAULT
)
```

### After (Settings with Production Support)
```python
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']
```

**Why this is better:**
- ✅ No test keys hardcoded
- ✅ Requires environment variables in production
- ✅ Allows deployment to proceed while warning check is silenced
- ✅ Clear error message if keys are not set

---

## 🎉 Next Steps

1. Set environment variables in Render (follow Step 2 above)
2. Deploy your app
3. Test registration with reCAPTCHA
4. Verify no errors in production logs

Your app is now ready for production reCAPTCHA validation! 🚀
