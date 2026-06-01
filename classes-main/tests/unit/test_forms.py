import pytest
from accounts.forms import UserRegisterForm
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_register_form_saves_phone(tmp_path, db):
    data = {
        'username': 'testuser',
        'password1': 'complexpassword123',
        'password2': 'complexpassword123',
        'email': 't@example.com',
        'phone': '+7 701 123 4567',
    }
    form = UserRegisterForm(data=data)
    assert form.is_valid(), form.errors.as_json()
    user = form.save()
    user.refresh_from_db()
    assert hasattr(user, 'profile')
    assert user.profile.phone == '+7 701 123 4567'


def test_user_register_form_rejects_invalid_phone():
    data = {
        'username': 'badphone',
        'password1': 'complexpassword123',
        'password2': 'complexpassword123',
        'email': 'b@example.com',
        'phone': 'invalid-phone!'
    }
    form = UserRegisterForm(data=data)
    assert not form.is_valid()
    assert 'phone' in form.errors
