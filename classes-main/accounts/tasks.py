import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_welcome_email_task(self, username, email):
    logger.info('Background task started: send welcome email for %s <%s>', username, email)
    if not email:
        logger.warning('Skipped welcome email, no email address provided for %s', username)
        return {'status': 'skipped', 'reason': 'missing_email'}

    subject = 'Добро пожаловать в Jobly'
    message = (
        f'Привет, {username}!\n\n'
        'Спасибо за регистрацию на Jobly. Мы рады видеть вас в системе.'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jobly.example.com')

    try:
        send_mail(subject, message, from_email, [email], fail_silently=False)
        logger.info('Welcome email queued for %s', email)
        return {'status': 'sent', 'email': email}
    except Exception as exc:
        logger.exception('Failed to send welcome email for %s', email)
        raise self.retry(exc=exc)

@shared_task(bind=True)
def process_resume_task(self, user_id, resume_text):
    logger.info('Started resume processing for user_id=%s', user_id)
    # Здесь можно подставить реальный парсер резюме, NLP или сторонний API.
    # Для демонстрации считаем, что обработка занимает время.
    import time
    time.sleep(5)
    parsed_resume = {
        'user_id': user_id,
        'length': len(resume_text),
        'keywords': ['Python', 'Django', 'SQL'],
    }
    logger.info('Finished resume processing for user_id=%s', user_id)
    return parsed_resume

@shared_task(bind=True)
def daily_job_digest_task(self):
    from .models import Job

    logger.info('Running daily job digest task')
    yesterday = timezone.now() - timedelta(days=1)
    jobs = Job.objects.filter(created_at__gte=yesterday).order_by('-created_at')[:20]
    if not jobs.exists():
        logger.info('No new jobs in the last 24 hours')
        return {'status': 'empty' }

    body = 'Новые вакансии за последние 24 часа:\n\n'
    for job in jobs:
        body += f'- {job.title} @ {job.company} ({job.location})\n'

    admin_email = getattr(settings, 'ADMINS', [('admin', 'admin@example.com')])[0][1]
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jobly.example.com')
    try:
        send_mail('Ежедневный дайджест вакансий Jobly', body, from_email, [admin_email], fail_silently=False)
        logger.info('Daily job digest sent to %s', admin_email)
        return {'status': 'sent', 'count': jobs.count()}
    except Exception as exc:
        logger.exception('Failed to send daily digest email')
        raise self.retry(exc=exc)

@shared_task(bind=True)
def cleanup_old_sessions_task(self):
    logger.info('Running cleanup_old_sessions_task')
    threshold = timezone.now() - timedelta(days=30)
    deleted, _ = Session.objects.filter(expire_date__lt=threshold).delete()
    logger.info('Deleted %s expired sessions older than 30 days', deleted)
    return {'deleted_sessions': deleted}
