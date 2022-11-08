# Generated by Django 4.1.2 on 2022-11-08 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_event_deadline_event_is_team_event_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('CP', 'Competition'), ('EV', 'Event')], default='EV', max_length=2),
        ),
    ]