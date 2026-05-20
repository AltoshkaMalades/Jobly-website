import pytest
import requests
from unittest.mock import Mock, patch

from accounts.ai_assistant import get_ai_response, OLLAMA_URL


@pytest.mark.django_db
def test_ai_assistant_successful_ollama_response():
    """Regression test for AI Service stability: Ollama returns a valid response payload."""

    def fake_post(url, *args, **kwargs):
        assert url == OLLAMA_URL
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"response": "Hello from Ollama"}
        return response

    with patch('accounts.ai_assistant.requests.post', side_effect=fake_post):
        assert get_ai_response('Hello') == 'Hello from Ollama'


@pytest.mark.django_db
def test_ai_chat_view_returns_successful_response(client):
    """Regression test for AI Service stability: AI chat endpoint returns a normal response on success."""
    with patch('accounts.ai_assistant.try_ollama', return_value='Ollama answer'):
        response = client.post('/ai-chat/', {'message': 'Hi there'})

    assert response.status_code == 200
    assert response.json() == {'response': 'Ollama answer'}


@pytest.mark.django_db
def test_ai_chat_rate_limit_exceeded_shows_friendly_message(client):
    """Regression test for AI Service stability: rate limit errors show friendly UI text instead of a 500 error."""

    mock_response = Mock()
    mock_response.status_code = 429
    http_error = requests.exceptions.HTTPError('429 Too Many Requests', response=mock_response)

    with patch('accounts.ai_assistant.try_ollama', return_value=None), \
         patch('accounts.ai_assistant.requests.post', side_effect=http_error):
        response = client.post('/ai-chat/', {'message': 'Please answer'})

    assert response.status_code == 200
    assert 'Rate limit' in response.json().get('response', '')
