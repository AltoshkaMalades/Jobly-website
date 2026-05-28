import logging

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_welcome_email_task(self, username, email):
    logger.info('Background task started: send welcome email for %s <%s>', username, email)
    # Здесь можно подключить реальную отправку email через Django send_mail
    return {'username': username, 'email': email}
