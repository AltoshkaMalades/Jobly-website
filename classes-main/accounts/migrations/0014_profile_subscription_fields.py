from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_remove_favorite_accounts_fa_user_id_6c6f24_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='subscription_purchased_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_refunded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_status',
            field=models.CharField(choices=[('not_purchased', 'Not purchased'), ('purchased', 'Purchased'), ('refunded', 'Refunded')], db_index=True, default='not_purchased', help_text='Purchased subscription access state', max_length=20),
        ),
    ]
