from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Константы ролей
ROLE_CHOICES = (
    ('student', 'Студент / Соискатель'),
    ('employer', 'Работодатель'),
    ('admin', 'Администратор'),
)

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('internship', 'Стажировка'),
        ('contract', 'Контракт'),
    )

    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    company = models.CharField(max_length=100, verbose_name="Компания")
    description = models.TextField(verbose_name="Описание")
    location = models.CharField(max_length=100, verbose_name="Локация")
    salary = models.CharField(max_length=50, blank=True, null=True, verbose_name="Зарплата")
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    category = models.CharField(max_length=100, verbose_name="Категория", db_index=True)
    requirements = models.TextField(blank=True, verbose_name="Требования")
    created_at = models.DateTimeField(auto_now_add=True)
    contact_email = models.EmailField(default="admin@example.com")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', db_index=True)

    SUBSCRIPTION_STATUS_CHOICES = (
        ('not_purchased', 'Not purchased'),
        ('purchased', 'Purchased'),
        ('refunded', 'Refunded'),
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default='not_purchased',
        db_index=True,
        help_text='Purchased subscription access state'
    )
    subscription_purchased_at = models.DateTimeField(null=True, blank=True)
    subscription_refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Поля для студента
    university = models.CharField(max_length=200, blank=True)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    
    # Поля для работодателя
    company_name = models.CharField(max_length=200, blank=True)
    
    # Общие поля
    bio = models.TextField(blank=True)
    # Телефон пользователя (используется регистрационной формой)
    phone = models.CharField(max_length=20, blank=True)
    # OAuth fields (added via migrations)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True, db_index=True)
    is_oauth_user = models.BooleanField(default=False, help_text='Вход через Google OAuth')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль: {self.user.username} ({self.get_role_display()})"

class Application(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Отправлено'), 
        ('viewed', 'Просмотрено'), 
        ('accepted', 'Принято'), 
        ('rejected', 'Отказ')
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_applications')
    cover_letter = models.TextField(verbose_name="Сопроводительное письмо")
    resume_file = models.FileField(upload_to='resumes/%Y/%m/', blank=True, null=True)
    resume_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'student')
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['student', 'status']),
        ]

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

# --- СИГНАЛЫ (Исправленные) ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль только при создании нового пользователя."""
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Безопасно сохраняет профиль при обновлении пользователя."""
    try:
        profile = instance.profile
    except Profile.DoesNotExist:
        return

    # Ensure we save the latest profile state, not a stale cached relation.
    try:
        profile.refresh_from_db()
    except Exception:
        pass

    profile.save()