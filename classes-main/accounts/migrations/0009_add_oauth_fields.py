"""
Generated migration for SEC-002 Google OAuth fields in Profile model
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_profile_company_name_alter_profile_role'),  # Adjust based on latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='google_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_oauth_user',
            field=models.BooleanField(default=False, help_text='Вход через Google OAuth'),
        ),
    ]
