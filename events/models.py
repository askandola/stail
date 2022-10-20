from django.db import models

from registrations.models import User

# Create your models here.

def eventImageUploadPath(instance, filename):
    return f"event/{instance.name}_{filename}"

class Event(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True, default=None)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=150, null=True, blank=True, default=None)
    image = models.ImageField(upload_to=eventImageUploadPath, null=True, blank=True, default=None)
    intra_thapar = models.BooleanField(blank=True, default=False)
    is_active = models.BooleanField(blank=True, default=True)

    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name
    
class Visit(models.Model):
    event = models.OneToOneField(Event, null=True, blank=True, default=None, on_delete=models.CASCADE)
    hits = models.IntegerField(blank=True, default=0)
