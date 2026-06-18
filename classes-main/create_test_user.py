import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# Create a test user
user, created = User.objects.get_or_create(
    username='testpayment',
    defaults={
        'email': 'testpayment@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✓ Created user: {user.username}")
else:
    user.set_password('testpass123')
    user.save()
    print(f"✓ User already exists (password reset): {user.username}")
