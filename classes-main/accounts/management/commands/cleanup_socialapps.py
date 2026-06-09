from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cleanup duplicate SocialApp entries and keep only one per provider'

    def handle(self, *args, **options):
        try:
            from allauth.socialaccount.models import SocialApp, SocialAppSite
            from django.contrib.sites.models import Site
        except ImportError:
            self.stdout.write(
                self.style.ERROR('django-allauth is not installed')
            )
            return

        # Get the current site
        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('No Site object found. Run: python manage.py migrate sites')
            )
            return

        # Get all providers
        providers = SocialApp.objects.values_list('provider', flat=True).distinct()

        for provider in providers:
            apps = SocialApp.objects.filter(provider=provider).order_by('-id')
            count = apps.count()

            if count > 1:
                self.stdout.write(
                    f"Found {count} {provider} SocialApp(s). Keeping the latest, removing duplicates..."
                )
                
                # Keep the first (latest) app, delete the rest
                keep_app = apps[0]
                delete_apps = apps[1:]

                for app in delete_apps:
                    # Remove app from all sites
                    SocialAppSite.objects.filter(app=app).delete()
                    # Delete the app
                    app.delete()
                    self.stdout.write(f"  ✓ Deleted duplicate {provider} app (ID: {app.id})")

                # Ensure the kept app is assigned to current site
                SocialAppSite.objects.get_or_create(
                    app=keep_app,
                    site=current_site
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Kept {provider} app (ID: {keep_app.id}) for site {current_site}")
                )
            elif count == 1:
                self.stdout.write(f"✓ {provider}: 1 app found (OK)")
            else:
                self.stdout.write(f"⚠ {provider}: No apps found")

        self.stdout.write(self.style.SUCCESS('\n✅ SocialApp cleanup completed!'))
