import pytest
from django.contrib.auth.models import User
from learning.models import Course, Lesson


@pytest.mark.django_db
@pytest.mark.parametrize('role', ['student', 'employer'])
def test_user_registration_with_role_selection(client, role):
    """User Intent: I want to sign up and choose whether I am a student or employer."""
    response = client.post(
        '/register/',
        data={
            'username': f'test_{role}',
            'email': f'test_{role}@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'role': role,
        }
    )

    # The user should be redirected to the home page after successful registration.
    assert response.status_code == 302
    assert response.url == '/'

    user = User.objects.get(username=f'test_{role}')
    assert user.profile.role == role


@pytest.mark.django_db
def test_course_list_and_lesson_detail_access(client):
    """User Intent: I want to browse available courses and open a lesson details page."""
    course = Course.objects.create(title='Test Course', desc='Course description', icon='🎓')
    lesson = Lesson.objects.create(course=course, title='First Lesson', rich_text_content='Lesson content')

    response = client.get('/learning/')
    assert response.status_code == 200
    assert 'Test Course' in response.content.decode('utf-8')

    lesson_response = client.get(f'/learning/lesson/{lesson.pk}/')
    assert lesson_response.status_code == 200
    lesson_text = lesson_response.content.decode('utf-8')
    assert 'First Lesson' in lesson_text
    assert 'Test Course' in lesson_text


@pytest.mark.django_db
def test_cv_download_returns_pdf(client):
    """User Intent: I want to download my CV as a valid PDF file."""
    user = User.objects.create_user(username='cvuser', password='TestPass123!')
    user.profile.role = 'student'
    user.profile.save()

    logged_in = client.login(username='cvuser', password='TestPass123!')
    assert logged_in is True

    response = client.get('/profile/cv/download/')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert response['Content-Disposition'] == 'attachment; filename="cvuser_cv.pdf"'
    assert response.content.startswith(b'%PDF')


@pytest.mark.django_db
def test_login_rate_limit_triggers_after_five_failed_attempts(client):
    User.objects.create_user(username='rateuser', password='TestPass123!')

    for _ in range(5):
        response = client.post('/login/', {'username': 'rateuser', 'password': 'WrongPass'})
        assert response.status_code == 200

    response = client.post('/login/', {'username': 'rateuser', 'password': 'WrongPass'})
    assert response.status_code == 429
    assert b'Too Many Requests' in response.content
