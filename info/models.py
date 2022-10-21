from django.db import models

from registrations.models import User
from events.models import Event

# Create your models here.

def sponsorImageUploadPath(instance, filename):
    return f"sponsor/{instance.name}_{filename}"

class Sponsor(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True, default=None)
    image = models.ImageField(upload_to=sponsorImageUploadPath, null=True, blank=True, default=None)

class Query(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_no = models.CharField(max_length=15)
    description = models.TextField()

class VerifyEndpoint(models.Model):
    endpoint = models.CharField(max_length=150)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
