import pytest
from django.core.cache import caches
from django.test import override_settings
from django.urls import reverse

@pytest.mark.django_db
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
def test_health_endpoint_ok(client):
    response = client.get(reverse('health'))
    assert response.status_code == 200
    data = response.json()
    assert data['database'] == 'ok'
    assert data['cache'] == 'ok'

@pytest.mark.django_db
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
def test_home_page_caches_html(client):
    caches['default'].clear()
    response1 = client.get(reverse('home'))
    assert response1.status_code == 200
    # Ensure cache key is set and subsequent responses are identical
    assert caches['default'].get('home_page_html') is not None
    response2 = client.get(reverse('home'))
    assert response2.content == response1.content

@pytest.mark.django_db
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
def test_search_page_is_cached_by_query(client):
    caches['default'].clear()
    response1 = client.get(reverse('search') + '?query=test')
    assert response1.status_code == 200
    response2 = client.get(reverse('search') + '?query=test')
    assert response2.content == response1.content
