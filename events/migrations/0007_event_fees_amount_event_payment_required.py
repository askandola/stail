# Generated by Django 4.1.2 on 2022-11-10 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_event_image_required_alter_event_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='fees_amount',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='event',
            name='payment_required',
            field=models.BooleanField(default=False),
        ),
    ]