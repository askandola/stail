# Generated by Django 4.1.2 on 2022-11-13 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_alter_event_category_alter_event_domain'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Visit',
        ),
    ]
