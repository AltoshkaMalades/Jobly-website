import pytest
from django.contrib.auth.models import User
from accounts.models import Profile # Убедись, что модель Profile существует в accounts

@pytest.fixture
def test_user(db):
    """Фикстура прямо в файле для надежности"""
    return User.objects.create_user(username="test_user_777", password="password123")

@pytest.mark.django_db
def test_user_role_assignment(test_user):
    # Действие: создаем/получаем профиль и ставим роль
    profile, created = Profile.objects.get_or_create(user=test_user)
    profile.role = 'student'
    profile.save()
    
    # Проверка: роль сохранилась?
    assert profile.role == 'student'
    assert profile.user.username == "test_user_777"