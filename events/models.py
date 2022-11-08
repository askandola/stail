from django.db import models

from registrations.models import User

# Create your models here.

def eventImageUploadPath(instance, filename):
    return f"event/{instance.name}_{filename}"

EVENT_TYPE_CHOICES = [
    ('CP','Competition'),
    ('EV', 'Event')
]

class Event(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True, default=None)
    image = models.ImageField(upload_to=eventImageUploadPath, null=True, blank=True, default=None)

    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=150, null=True, blank=True, default=None)

    type = models.CharField(max_length=2, choices=EVENT_TYPE_CHOICES, default='EV')
    intra_thapar = models.BooleanField(blank=True, default=False)

    deadline = models.DateTimeField(blank=True, null=True, default=None)
    is_active = models.BooleanField(blank=True, default=True)

    verification_required = models.BooleanField(blank=True, default=False)

    is_team_event = models.BooleanField(default=False)  #True for team based events
    min_team_size = models.SmallIntegerField(null=True, blank=True, default=None)
    max_team_size = models.SmallIntegerField(null=True, blank=True, default=None)

    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leader_team_set')
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name+'_'+self.event.name

class Visit(models.Model):
    event = models.OneToOneField(Event, null=True, blank=True, default=None, on_delete=models.CASCADE)
    hits = models.IntegerField(blank=True, default=0)
