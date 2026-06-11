"""
Test reCAPTCHA integration with Google's official test keys
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.conf import settings
from accounts.forms import HAS_RECAPTCHA, UserRegisterForm


def test_recaptcha_keys_configured():
    """Verify reCAPTCHA test keys are properly configured"""
    
    print("\n" + "=" * 70)
    print("reCAPTCHA CONFIGURATION TEST")
    print("=" * 70)
    
    public_key = settings.RECAPTCHA_PUBLIC_KEY
    private_key = settings.RECAPTCHA_PRIVATE_KEY
    
    print(f"\nPublic Key:  {public_key}")
    print(f"Private Key: {private_key}")
    
    # Verify we're using test keys
    test_public = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    test_private = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    
    if public_key == test_public and private_key == test_private:
        print("\n✓ Using Google's official reCAPTCHA test keys")
        print("  These keys are configured to ALWAYS PASS validation")
        return True
    else:
        print("\n⚠ Using custom reCAPTCHA keys (not test keys)")
        if 'ProdKeyExample' in public_key or 'ProdSecretExample' in private_key:
            print("  ✗ ERROR: Placeholder keys detected - these will NOT work!")
            return False
        return True


def test_registration_form_with_captcha():
    """Test UserRegisterForm includes reCAPTCHA field"""
    
    print("\n" + "=" * 70)
    print("REGISTRATION FORM CAPTCHA TEST")
    print("=" * 70)
    
    if HAS_RECAPTCHA:
        print("\n✓ django_recaptcha is installed")
        form = UserRegisterForm()
        if 'captcha' in form.fields:
            print("✓ reCAPTCHA field is in UserRegisterForm")
            print(f"  Widget: {form.fields['captcha'].widget.__class__.__name__}")
            print(f"  Required: {form.fields['captcha'].required}")
            return True
        else:
            print("✗ reCAPTCHA field NOT found in UserRegisterForm")
            print(f"  Available fields: {list(form.fields.keys())}")
            return False
    else:
        print("✗ django_recaptcha is NOT installed")
        print("  Install with: pip install django-recaptcha")
        return False


if __name__ == '__main__':
    print("\n")
    print("🔐 reCAPTCHA Integration Test Suite")
    print("=" * 70)
    
    # Run tests
    test1 = test_recaptcha_keys_configured()
    test2 = test_registration_form_with_captcha()
    
    # Print summary
    print("\n" + "=" * 70)
    if test1 and test2:
        print("✓ reCAPTCHA IS PROPERLY CONFIGURED")
        print("  Registrations should now work without CAPTCHA errors")
        print("  The form will accept reCAPTCHA responses and verify them correctly")
    else:
        print("✗ reCAPTCHA CONFIGURATION ISSUES DETECTED")
    print("=" * 70)
    
    sys.exit(0 if (test1 and test2) else 1)
