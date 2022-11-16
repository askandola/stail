# Generated by Django 4.1.2 on 2022-11-16 04:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_event_curr_female_count_event_curr_male_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='rules_array',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1000), default=None, size=None),
            preserve_default=False,
        ),
    ]