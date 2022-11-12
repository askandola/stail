# Generated by Django 4.1.2 on 2022-11-12 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_remove_event_users_eventusertable'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('TL', 'Technical'), ('CL', 'Cultural')], default=None, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='domain',
            field=models.CharField(choices=[('MS', 'Music'), ('DC', 'Dance'), ('FS', 'Fashion'), ('AT', 'Acting'), ('PT', 'Poetry'), ('CM', 'Comedy'), ('TL', 'Talent'), ('AR', 'Art'), ('EL', 'Electronics'), ('CP', 'Computers'), ('RB', 'Robotics')], default=None, max_length=3, null=True),
        ),
    ]
