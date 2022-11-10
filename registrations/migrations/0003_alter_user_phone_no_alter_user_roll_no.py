# Generated by Django 4.1.2 on 2022-11-09 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0002_user_is_verified_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_no',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='roll_no',
            field=models.CharField(blank=True, default=None, max_length=15, null=True, unique=True),
        ),
    ]