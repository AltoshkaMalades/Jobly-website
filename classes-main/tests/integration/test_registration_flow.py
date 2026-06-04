import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_registration_view(client):
    # Симулируем переход на страницу регистрации
    url = reverse('register')
    response = client.get(url)

    assert response.status_code == 200
    assert "Create your account" in response.content.decode()

@pytest.mark.django_db
def test_registration_saves_phone_and_shows_profile(client):
    url = reverse('register')
    data = {
        'username': 'profilephone',
        'email': 'profilephone@example.com',
        'password1': 'StrongPass123!',
        'password2': 'StrongPass123!',
        'role': 'student',
        'phone': '+7 701 987 6543',
        'captcha_expected': '123456',
        'captcha_input': '123456',
    }
    response = client.post(url, data)
    assert response.status_code == 302

    user = User.objects.get(username='profilephone')
    assert user.profile.phone == '+7 701 987 6543'

    client.force_login(user)
    profile_response = client.get(reverse('profile'))
    assert profile_response.status_code == 200
    assert '+7 701 987 6543' in profile_response.content.decode()