# Generated by Django 4.1.2 on 2022-11-10 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_event_payment_required_alter_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image_url',
            field=models.URLField(default=None, max_length=5000, null=True),
        ),
    ]
