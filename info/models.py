from django.db import models

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
    phone = models.CharField(max_length=15)
    description = models.TextField()
