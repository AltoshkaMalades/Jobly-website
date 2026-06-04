import os

# Ensure Django test mode is detected early for pytest runs.
os.environ.setdefault('DJANGO_TESTING', '1')
