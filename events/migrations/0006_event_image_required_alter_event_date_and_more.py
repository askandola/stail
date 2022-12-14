# Generated by Django 4.1.2 on 2022-11-09 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_rule'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
    ]
