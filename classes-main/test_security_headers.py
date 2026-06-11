"""
Test script to verify security headers are properly set by middleware
"""
import os
import sys
import django
from django.test import TestCase, RequestFactory
from django.http import HttpResponse

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from core.middleware import SecurityHeadersMiddleware


def test_security_headers():
    """Test that SecurityHeadersMiddleware sets all required headers"""
    
    # Create a mock view that returns a simple response
    def get_response(request):
        return HttpResponse("Test response")
    
    # Initialize the middleware
    middleware = SecurityHeadersMiddleware(get_response)
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Process the request through middleware
    response = middleware(request)
    
    print("=" * 70)
    print("SECURITY HEADERS VERIFICATION TEST")
    print("=" * 70)
    
    # Check each header
    headers_to_check = [
        'Strict-Transport-Security',
        'Content-Security-Policy',
        'Permissions-Policy'
    ]
    
    all_present = True
    for header in headers_to_check:
        if header in response:
            print(f"✓ {header}: PRESENT")
            print(f"  Value: {response[header][:80]}{'...' if len(response[header]) > 80 else ''}")
        else:
            print(f"✗ {header}: MISSING")
            all_present = False
    
    print("\n" + "=" * 70)
    
    # Detailed check for each header
    print("\nDETAILED HEADER VALUES:\n")
    
    if 'Strict-Transport-Security' in response:
        print("Strict-Transport-Security:")
        print(f"  {response['Strict-Transport-Security']}")
        # Verify recommended value
        if 'max-age=31536000' in response['Strict-Transport-Security'] and 'includeSubDomains' in response['Strict-Transport-Security']:
            print("  ✓ Contains recommended values (max-age=31536000 and includeSubDomains)")
        else:
            print("  ⚠ May not contain recommended values")
    
    if 'Content-Security-Policy' in response:
        print("\nContent-Security-Policy:")
        csp = response['Content-Security-Policy']
        print(f"  {csp[:150]}...")
        if 'default-src' in csp:
            print("  ✓ Contains default-src directive")
        if 'script-src' in csp:
            print("  ✓ Contains script-src directive")
        if 'style-src' in csp:
            print("  ✓ Contains style-src directive")
    
    if 'Permissions-Policy' in response:
        print("\nPermissions-Policy:")
        print(f"  {response['Permissions-Policy']}")
        if 'camera=()' in response['Permissions-Policy']:
            print("  ✓ Camera disabled")
        if 'microphone=()' in response['Permissions-Policy']:
            print("  ✓ Microphone disabled")
        if 'geolocation=()' in response['Permissions-Policy']:
            print("  ✓ Geolocation disabled")
    
    print("\n" + "=" * 70)
    if all_present:
        print("✓ ALL SECURITY HEADERS PRESENT AND CONFIGURED")
    else:
        print("✗ SOME SECURITY HEADERS ARE MISSING")
    print("=" * 70)
    
    return all_present


if __name__ == '__main__':
    success = test_security_headers()
    sys.exit(0 if success else 1)
