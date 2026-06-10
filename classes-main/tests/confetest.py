import pytest
import os
import django
from django.contrib.auth.models import User
from django.test import Client

# Configure SQLite for testing (before Django setup)
# This overrides DATABASE_URL from .env if it points to PostgreSQL
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')

from accounts.models import Job, Profile

try:
    from rest_framework.test import APIClient
except ImportError:
    APIClient = Client

@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="test_serikbay",
        password="password123",
        email="test_serikbay@example.com",
    )

@pytest.fixture
def employer_user(db):
    user = User.objects.create_user(
        username="employer_user",
        password="password123",
        email="employer@example.com",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.role = 'employer'
    profile.company_name = 'ACME Recruiting'
    profile.save()
    return user

@pytest.fixture
def student_user(db):
    user = User.objects.create_user(
        username="student_user",
        password="password123",
        email="student@example.com",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.role = 'student'
    profile.save()
    return user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(client, test_user):
    client.login(username=test_user.username, password='password123')
    return client

@pytest.fixture
def employer_client(client, employer_user):
    client.login(username=employer_user.username, password='password123')
    return client

@pytest.fixture
def basic_company(db, employer_user):
    return {
        'name': employer_user.profile.company_name or 'ACME Recruiting',
        'contact_email': 'recruit@example.com',
        'employer': employer_user,
    }

@pytest.fixture
def basic_job(db, employer_user):
    return Job.objects.create(
        employer=employer_user,
        title='Junior Python Developer',
        company=employer_user.profile.company_name or 'ACME Recruiting',
        description='Тестовая вакансия для проверки логики.',
        location='Алматы',
        salary='400 000 KZT',
        category='Software',
        contact_email='jobs@example.com',
    )
    