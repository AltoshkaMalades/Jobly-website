from django.core.management.base import BaseCommand

from learning.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает примерный курс и урок для раздела learning.'

    def handle(self, *args, **options):
        course, course_created = Course.objects.get_or_create(
            title='CV Mastery',
            defaults={
                'desc': 'Курс, который поможет создать профессиональное резюме и подготовиться к собеседованиям.',
                'icon': '📄',
            }
        )

        lesson_data = {
            'video_url': 'https://www.youtube.com/watch?v=Xp6iL_OcWEw',
            'rich_text_content': (
                '<p>В этом уроке вы узнаете, как построить идеальное CV:</p>'
                '<ul>'
                '<li>Выделите ключевые навыки и достижения</li>'
                '<li>Напишите понятное и краткое резюме</li>'
                '<li>Укажите образование и опыт в правильном порядке</li>'
                '<li>Приведите примеры проектов и результатов</li>'
                '</ul>'
                '<p>Используйте этот шаблон как основу для профессионального CV.</p>'
            ),
        }

        lesson, lesson_created = Lesson.objects.update_or_create(
            title='How to build a perfect CV',
            course=course,
            defaults=lesson_data,
        )

        if course_created:
            self.stdout.write(self.style.SUCCESS(f'Курс создан: {course.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Курс уже существует: {course.title}'))

        if lesson_created:
            self.stdout.write(self.style.SUCCESS(f'Урок создан: {lesson.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Урок обновлен: {lesson.title}'))
