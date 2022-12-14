# Generated by Django 4.1.2 on 2022-10-23 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0002_verifyendpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifyendpoint',
            name='url',
            field=models.URLField(blank=True, default=None, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='verifyendpoint',
            name='endpoint',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
