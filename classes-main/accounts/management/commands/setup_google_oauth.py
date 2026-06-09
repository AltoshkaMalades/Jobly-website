from django.core.management.base import BaseCommand
from django.db import transaction
import os


class Command(BaseCommand):
    help = 'Автоматически создает или обновляет Google OAuth приложение и привязывает его к сайту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            default=os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '909443104126-baj9tq8uhj7tb6fg3vv8d9vvg03c7qr4.apps.googleusercontent.com'),
            help='Google OAuth Client ID (or env var GOOGLE_OAUTH_CLIENT_ID)',
        )
        parser.add_argument(
            '--secret',
            type=str,
            default=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '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'),
            help='Google OAuth Client Secret (or env var GOOGLE_OAUTH_CLIENT_SECRET)',
        )
        parser.add_argument(
            '--domain',
            type=str,
            default=os.environ.get('SITE_DOMAIN', 'jobly.kz'),
            help='Domain name для Site (or env var SITE_DOMAIN)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp
        except ImportError as e:
            self.stdout.write(self.style.ERROR(
                f"❌ Required module not available: {e}. "
                "Install django-allauth with: pip install django-allauth"
            ))
            return
        
        client_id = options['client_id']
        secret = options['secret']
        domain = options['domain']
        site_id = 1

        # Шаг 1: Получить или создать Site с id=1
        try:
            site = Site.objects.get(id=site_id)
            self.stdout.write(f"✓ Site с id={site_id} существует: {site.domain}")
            
            # Обновить домен если нужно
            if site.domain != domain:
                old_domain = site.domain
                site.domain = domain
                site.name = domain
                site.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  Домен обновлен: {old_domain} → {domain}"
                ))
        except Site.DoesNotExist:
            site = Site.objects.create(
                id=site_id,
                domain=domain,
                name=domain,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Site создан: {domain}"))

        # Шаг 2: Получить или создать SocialApplication для Google
        try:
            # Handle MultipleObjectsReturned by using filter + first
            try:
                app = SocialApp.objects.get(provider='google')
            except SocialApp.MultipleObjectsReturned:
                self.stdout.write(self.style.WARNING(
                    "⚠️ Multiple Google SocialApps found! Using the most recent one."
                ))
                app = SocialApp.objects.filter(provider='google').order_by('-id').first()
                if not app:
                    raise SocialApp.DoesNotExist("No Google SocialApp found after MultipleObjectsReturned")
            
            self.stdout.write(f"✓ Google SocialApp существует: {app.name}")
            
            # Обновить credentials если они отличаются
            updated = False
            if app.client_id != client_id:
                app.client_id = client_id
                updated = True
            if app.secret != secret:
                app.secret = secret
                updated = True
                
            if updated:
                app.save()
                self.stdout.write(self.style.SUCCESS(
                    "  Credentials обновлены"
                ))
        except SocialApp.DoesNotExist:
            app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth',
                client_id=client_id,
                secret=secret,
            )
            self.stdout.write(self.style.SUCCESS(
                f"✓ Google SocialApp создан"
            ))

        # Шаг 3: Привязать приложение к сайту
        # SocialApp имеет ManyToMany поле к Site
        if not app.sites.filter(id=site_id).exists():
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(
                f"✓ SocialApp привязан к Site: {site.domain}"
            ))
        else:
            self.stdout.write(f"✓ SocialApp уже привязан к Site: {site.domain}")

        self.stdout.write(self.style.SUCCESS(
            "\n✅ Конфигурация Google OAuth завершена успешно!"
        ))
