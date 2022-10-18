# Generated by Django 4.1.2 on 2022-10-18 17:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import events.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('venue', models.CharField(blank=True, default=None, max_length=150, null=True)),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to=events.models.eventImageUploadPath)),
                ('intra_thapar', models.BooleanField(blank=True, default=False)),
                ('is_active', models.BooleanField(blank=True, default=True)),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hits', models.IntegerField(blank=True, default=0)),
                ('event', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
    ]
