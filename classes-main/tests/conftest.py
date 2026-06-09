import os
import pytest
from unittest.mock import patch

# Ensure Django test mode is detected early for pytest runs.
os.environ.setdefault('DJANGO_TESTING', '1')


@pytest.fixture(autouse=True)
def mock_recaptcha():
    """Mock reCAPTCHA validation in tests to avoid external API calls."""
    try:
        from django_recaptcha.fields import ReCaptchaField
        with patch.object(ReCaptchaField, 'clean', return_value=None):
            yield
    except ImportError:
        # django-recaptcha not installed
        yield
