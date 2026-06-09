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
        total_deleted = 0

        for provider in providers:
            apps = SocialApp.objects.filter(provider=provider).order_by('-id')
            count = apps.count()

            if count > 1:
                self.stdout.write(
                    self.style.WARNING(f"\n⚠️ Found {count} {provider} SocialApp(s). Keeping the latest, removing {count-1} duplicate(s)...")
                )
                
                # Keep the first (latest) app, delete the rest
                keep_app = apps[0]
                delete_apps = list(apps[1:])

                for app in delete_apps:
                    try:
                        # Remove app from all sites
                        deleted_sites = SocialAppSite.objects.filter(app=app).delete()
                        self.stdout.write(f"  ├─ Removed {app.id} from {deleted_sites[0]} site(s)")
                        
                        # Delete the app
                        app_id = app.id
                        app.delete()
                        self.stdout.write(f"  └─ ✓ Deleted duplicate {provider} app (ID: {app_id})")
                        total_deleted += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Error deleting {provider} app {app.id}: {str(e)}")
                        )

                # Ensure the kept app is assigned to current site
                try:
                    site_link, created = SocialAppSite.objects.get_or_create(
                        app=keep_app,
                        site=current_site
                    )
                    action = "Created" if created else "Verified existing"
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {action} link for {provider} app (ID: {keep_app.id}) to site {current_site}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error linking {provider} app to site: {str(e)}")
                    )
            elif count == 1:
                app = apps[0]
                # Ensure it's linked to current site
                try:
                    SocialAppSite.objects.get_or_create(
                        app=app,
                        site=current_site
                    )
                    self.stdout.write(f"✓ {provider}: 1 app found (OK) - linked to {current_site}")
                except Exception as e:
                    self.stdout.write(f"⚠ {provider}: Error linking app to site: {str(e)}")
            else:
                self.stdout.write(f"⚠ {provider}: No apps found (will be created by setup_google_oauth)")

        if total_deleted > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ SocialApp cleanup completed! Deleted {total_deleted} duplicate app(s).')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ SocialApp cleanup completed! No duplicates found.')
            )
