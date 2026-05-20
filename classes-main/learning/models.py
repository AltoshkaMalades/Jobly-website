from django.db import models
from embed_video.fields import EmbedVideoField


class Course(models.Model):
    title = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text='Emoji или CSS-иконка для курса, например: 🎓',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = EmbedVideoField(blank=True)
    rich_text_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return f'{self.title} — {self.course.title}'
