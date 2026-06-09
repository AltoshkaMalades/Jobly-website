from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.db import transaction


class Command(BaseCommand):
    help = 'Автоматически создает или обновляет Google OAuth приложение и привязывает его к сайту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            default='909443104126-baj9tq8uhj7tb6fg3vv8d9vvg03c7qr4.apps.googleusercontent.com',
            help='Google OAuth Client ID',
        )
        parser.add_argument(
            '--secret',
            type=str,
            default='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',
            help='Google OAuth Client Secret',
        )
        parser.add_argument(
            '--domain',
            type=str,
            default='jobly.kz',
            help='Domain name для Site',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            from allauth.socialaccount.models import SocialApp
        except ImportError:
            self.stdout.write(self.style.ERROR(
                "❌ django-allauth is not installed. Install it with: pip install django-allauth"
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
            app = SocialApp.objects.get(provider='google')
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
