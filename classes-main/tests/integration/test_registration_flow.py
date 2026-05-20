import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_registration_view(client):
    # Симулируем переход на страницу регистрации
    url = reverse('register') # Убедись, что имя в urls.py совпадает
    response = client.get(url)
    
    assert response.status_code == 200
    assert "Create your account" in response.content.decode()