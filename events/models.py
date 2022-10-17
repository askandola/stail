from django.db import models

from registrations.models import User

# Create your models here.

def uploadPath(instance, filename):
    return f"event/{instance.name}_{filename}"

class Event(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(default="")
    date = models.DateField()
    time = models.TimeField()
    # venue = models.CharField(max_length=150) to be discussed
    image = models.ImageField(upload_to=uploadPath, null=True, blank=True, default=None) #defaut for image url, to be discussed
    intra_thapar = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=True) to be discussed

    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name
    
class total_views(models.Model):
    hits=models.IntegerField(default=0)
