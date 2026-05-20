import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from accounts.models import Job, Profile, Application, Favorite
from learning.models import Course, Lesson


# ===== ACCOUNTS APP MODEL TESTS =====

@pytest.mark.django_db
def test_job_creation():
    """Test basic Job model creation and field assignment."""
    user = User.objects.create_user(username='test_employer')

    job = Job.objects.create(
        title="Python Developer",
        employer=user,
        description="Developing cool stuff",
        category="IT"
    )

    assert job.title == "Python Developer"
    assert job.employer.username == "test_employer"
    assert Job.objects.count() == 1


@pytest.mark.django_db
def test_job_field_constraints():
    """Test Job model field constraints including max_length and blank/null fields."""
    user = User.objects.create_user(username='employer')

    # Test max_length constraints
    job = Job.objects.create(
        title="A" * 200,  # Max length is 200
        employer=user,
        company="A" * 100,  # Max length is 100
        description="Test description",
        location="A" * 100,  # Max length is 100
        category="A" * 100,  # Max length is 100
        salary="A" * 50,  # Max length is 50
    )

    # Should save successfully
    assert job.title == "A" * 200
    assert job.company == "A" * 100
    assert job.location == "A" * 100
    assert job.category == "A" * 100
    assert job.salary == "A" * 50

    # Test blank/null fields
    job_blank = Job.objects.create(
        title="Test Job",
        employer=user,
        description="Test",
        category="Test",
        salary=None  # Should allow null
    )
    assert job_blank.salary is None


@pytest.mark.django_db
def test_job_string_representation():
    """Test Job model string representation (__str__ method)."""
    user = User.objects.create_user(username='employer')
    job = Job.objects.create(
        title="Senior Developer",
        employer=user,
        company="Tech Corp",
        description="Great job",
        category="IT"
    )

    assert str(job) == "Senior Developer @ Tech Corp"


@pytest.mark.django_db
def test_job_ordering():
    """Test Job model ordering by created_at (descending)."""
    user = User.objects.create_user(username='employer')

    job1 = Job.objects.create(title="Job 1", employer=user, description="Desc", category="IT")
    job2 = Job.objects.create(title="Job 2", employer=user, description="Desc", category="IT")

    jobs = list(Job.objects.all())
    # Should be ordered by -created_at (newest first)
    assert jobs[0] == job2
    assert jobs[1] == job1


@pytest.mark.django_db
def test_profile_creation_signal():
    """Test that Profile is automatically created when User is created via signal."""
    user = User.objects.create_user(username='testuser', email='test@example.com')

    # Profile should be created automatically via signal
    assert hasattr(user, 'profile')
    assert user.profile.role == 'student'  # Default role
    assert Profile.objects.count() == 1


@pytest.mark.django_db
def test_profile_field_constraints():
    """Test Profile model field constraints including max_length and blank fields."""
    user = User.objects.create_user(username='testuser1')

    # Get the profile created by signal and update it
    profile = user.profile
    profile.role = 'student'
    profile.university = "A" * 200  # Max length is 200
    profile.company_name = "A" * 200  # Max length is 200
    profile.education = "Test education"
    profile.experience = "Test experience"
    profile.skills = "Test skills"
    profile.summary = "Test summary"
    profile.bio = "Test bio"
    profile.save()

    # Should save successfully
    assert profile.university == "A" * 200
    assert profile.company_name == "A" * 200

    # Test blank fields (should allow blank)
    user2 = User.objects.create_user(username='testuser2')
    profile_blank = user2.profile
    profile_blank.role = 'employer'
    # All other fields remain blank
    profile_blank.save()

    assert profile_blank.university == ""
    assert profile_blank.bio == ""


@pytest.mark.django_db
def test_profile_role_choices():
    """Test Profile role field choices and validation."""
    # Test valid roles
    for i, role in enumerate(['student', 'employer', 'admin']):
        user = User.objects.create_user(username=f'testuser_role_{i}')
        profile = user.profile
        profile.role = role
        profile.save()

        assert profile.role == role
        assert profile.get_role_display() in ['Студент / Соискатель', 'Работодатель', 'Администратор']


@pytest.mark.django_db
def test_profile_string_representation():
    """Test Profile model string representation (__str__ method)."""
    user = User.objects.create_user(username='testuser_repr')
    profile = user.profile
    profile.role = 'student'
    profile.save()

    assert str(profile) == "Профиль: testuser_repr (Студент / Соискатель)"


@pytest.mark.django_db
def test_profile_role_assignment_logic():
    """Test Profile role assignment logic and default values."""
    user = User.objects.create_user(username='testuser')

    # Test default role assignment via signal
    assert user.profile.role == 'student'

    # Test manual role assignment
    user.profile.role = 'employer'
    user.profile.save()
    user.profile.refresh_from_db()
    assert user.profile.role == 'employer'

    # Test role display names
    assert user.profile.get_role_display() == 'Работодатель'


@pytest.mark.django_db
def test_application_creation():
    """Test Application model creation and basic functionality."""
    employer = User.objects.create_user(username='employer')
    student = User.objects.create_user(username='student')

    job = Job.objects.create(
        title="Test Job",
        employer=employer,
        description="Test",
        category="IT"
    )

    application = Application.objects.create(
        job=job,
        student=student,
        cover_letter="I want this job!"
    )

    assert application.job == job
    assert application.student == student
    assert application.cover_letter == "I want this job!"
    assert application.status == 'sent'  # Default status


@pytest.mark.django_db
def test_application_unique_constraint():
    """Test Application model unique_together constraint (job, student)."""
    employer = User.objects.create_user(username='employer')
    student = User.objects.create_user(username='student')

    job = Job.objects.create(
        title="Test Job",
        employer=employer,
        description="Test",
        category="IT"
    )

    # Create first application
    Application.objects.create(
        job=job,
        student=student,
        cover_letter="First application"
    )

    # Try to create duplicate - should raise IntegrityError
    with pytest.raises(IntegrityError):
        Application.objects.create(
            job=job,
            student=student,
            cover_letter="Duplicate application"
        )


@pytest.mark.django_db
def test_application_status_choices():
    """Test Application status field choices."""
    employer = User.objects.create_user(username='employer')
    student = User.objects.create_user(username='student')

    job = Job.objects.create(
        title="Test Job",
        employer=employer,
        description="Test",
        category="IT"
    )

    # Test all valid statuses
    for status in ['sent', 'viewed', 'accepted', 'rejected']:
        app = Application.objects.create(
            job=job,
            student=student,
            cover_letter="Test",
            status=status
        )
        assert app.status == status
        assert app.get_status_display() in ['Отправлено', 'Просмотрено', 'Принято', 'Отказ']
        app.delete()


@pytest.mark.django_db
def test_favorite_creation():
    """Test Favorite model creation and basic functionality."""
    user = User.objects.create_user(username='user')
    employer = User.objects.create_user(username='employer')

    job = Job.objects.create(
        title="Test Job",
        employer=employer,
        description="Test",
        category="IT"
    )

    favorite = Favorite.objects.create(user=user, job=job)

    assert favorite.user == user
    assert favorite.job == job
    assert Favorite.objects.count() == 1


@pytest.mark.django_db
def test_favorite_unique_constraint():
    """Test Favorite model unique_together constraint (user, job)."""
    user = User.objects.create_user(username='user')
    employer = User.objects.create_user(username='employer')

    job = Job.objects.create(
        title="Test Job",
        employer=employer,
        description="Test",
        category="IT"
    )

    # Create first favorite
    Favorite.objects.create(user=user, job=job)

    # Try to create duplicate - should raise IntegrityError
    with pytest.raises(IntegrityError):
        Favorite.objects.create(user=user, job=job)


# ===== LEARNING APP MODEL TESTS =====

@pytest.mark.django_db
def test_course_creation():
    """Test Course model creation and basic functionality."""
    course = Course.objects.create(
        title="Python Basics",
        desc="Learn Python fundamentals",
        icon="🐍"
    )

    assert course.title == "Python Basics"
    assert course.desc == "Learn Python fundamentals"
    assert course.icon == "🐍"
    assert Course.objects.count() == 1


@pytest.mark.django_db
def test_course_field_constraints():
    """Test Course model field constraints including max_length and blank fields."""
    # Test max_length constraints
    course = Course.objects.create(
        title="A" * 200,  # Max length is 200
        desc="Test description",
        icon="A" * 100  # Max length is 100
    )

    assert course.title == "A" * 200
    assert course.icon == "A" * 100

    # Test blank fields
    course_blank = Course.objects.create(
        title="Test Course"
        # desc and icon can be blank
    )
    assert course_blank.desc == ""
    assert course_blank.icon == ""


@pytest.mark.django_db
def test_course_string_representation():
    """Test Course model string representation (__str__ method)."""
    course = Course.objects.create(title="Advanced Python")
    assert str(course) == "Advanced Python"


@pytest.mark.django_db
def test_course_ordering():
    """Test Course model ordering by title (ascending)."""
    course1 = Course.objects.create(title="B Course")
    course2 = Course.objects.create(title="A Course")

    courses = list(Course.objects.all())
    # Should be ordered by title (alphabetical)
    assert courses[0] == course2  # "A Course"
    assert courses[1] == course1  # "B Course"


@pytest.mark.django_db
def test_lesson_creation():
    """Test Lesson model creation and foreign key relationship."""
    course = Course.objects.create(title="Test Course")

    lesson = Lesson.objects.create(
        course=course,
        title="Introduction",
        rich_text_content="<p>Welcome to the course!</p>"
    )

    assert lesson.course == course
    assert lesson.title == "Introduction"
    assert lesson.rich_text_content == "<p>Welcome to the course!</p>"
    assert Lesson.objects.count() == 1


@pytest.mark.django_db
def test_lesson_field_constraints():
    """Test Lesson model field constraints including max_length and blank fields."""
    course = Course.objects.create(title="Test Course")

    lesson = Lesson.objects.create(
        course=course,
        title="A" * 200,  # Max length is 200
        rich_text_content="Test content"
        # video_url can be blank
    )

    assert lesson.title == "A" * 200

    # Test blank fields
    lesson_blank = Lesson.objects.create(
        course=course,
        title="Blank Lesson"
        # video_url and rich_text_content can be blank
    )
    assert lesson_blank.video_url == ""
    assert lesson_blank.rich_text_content == ""


@pytest.mark.django_db
def test_lesson_string_representation():
    """Test Lesson model string representation (__str__ method)."""
    course = Course.objects.create(title="Python Course")
    lesson = Lesson.objects.create(
        course=course,
        title="Variables"
    )

    assert str(lesson) == "Variables — Python Course"


@pytest.mark.django_db
def test_lesson_cascade_delete():
    """Test that lessons are deleted when course is deleted (CASCADE)."""
    course = Course.objects.create(title="Test Course")
    lesson = Lesson.objects.create(course=course, title="Test Lesson")

    assert Lesson.objects.count() == 1

    # Delete course
    course.delete()

    # Lesson should be deleted too
    assert Lesson.objects.count() == 0


@pytest.mark.django_db
def test_lesson_related_name():
    """Test Lesson model's related_name 'lessons' on Course."""
    course = Course.objects.create(title="Test Course")

    lesson1 = Lesson.objects.create(course=course, title="Lesson 1")
    lesson2 = Lesson.objects.create(course=course, title="Lesson 2")

    # Test reverse relationship
    assert course.lessons.count() == 2
    assert lesson1 in course.lessons.all()
    assert lesson2 in course.lessons.all()


@pytest.mark.django_db
def test_lesson_ordering():
    """Test Lesson model ordering by title (ascending)."""
    course = Course.objects.create(title="Test Course")

    lesson1 = Lesson.objects.create(course=course, title="B Lesson")
    lesson2 = Lesson.objects.create(course=course, title="A Lesson")

    lessons = list(Lesson.objects.all())
    # Should be ordered by title (alphabetical)
    assert lessons[0] == lesson2  # "A Lesson"
    assert lessons[1] == lesson1  # "B Lesson"