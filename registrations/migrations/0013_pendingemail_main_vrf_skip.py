# Generated by Django 4.1.2 on 2022-11-20 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0012_pendingemail_event_pendingemail_fees_per_member_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingemail',
            name='main_vrf_skip',
            field=models.BooleanField(default=False),
        ),
    ]