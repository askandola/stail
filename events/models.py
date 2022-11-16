from django.db import models
from django.core.cache import cache
from django.contrib.postgres.fields import ArrayField

from registrations.models import User

# Create your models here.

def eventImageUploadPath(instance, filename):
    return f"event/{instance.name}_{filename}"

EVENT_TYPE_CHOICES = [
    ('CP','Competition'),
    ('EV', 'Event')
]

EVENT_CATEGORY_CHOICES = [
    ('TL', 'Technical'),
    ('CL', 'Cultural')
]

EVENT_DOMAIN_CHOICES = [
    ('MS', 'Music'),
    ('DC', 'Dance'),
    ('FS', 'Fashion'),
    ('AT', 'Acting'),
    ('PT', 'Poetry'),
    ('CM', 'Comedy'),
    ('TL', 'Talent'),
    ('AR', 'Art'),
    ('EL', 'Electronics'),
    ('CP', 'Computers'),
    ('RB', 'Robotics')
]

class Event(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True, default=None)

    # image_required = models.BooleanField(default=False)
    # image = models.ImageField(upload_to=eventImageUploadPath, null=True, default=None)
    image_url = models.URLField(max_length=5000, null=True, default=None)

    date = models.DateField(null=True, blank=True, default=None)
    time = models.TimeField(null=True, blank=True, default=None)
    venue = models.CharField(max_length=150, null=True, blank=True, default=None)

    type = models.CharField(max_length=2, choices=EVENT_TYPE_CHOICES, default='EV')
    intra_thapar = models.BooleanField(blank=True, default=False)
    category = models.CharField(max_length=2, choices=EVENT_CATEGORY_CHOICES, blank=True, null=True, default=None)
    domain = models.CharField(max_length=3, choices=EVENT_DOMAIN_CHOICES, blank=True, null=True, default=None)

    deadline = models.DateTimeField(blank=True, null=True, default=None)
    is_active = models.BooleanField(blank=True, default=True)

    fees_amount = models.IntegerField(default=0, blank=True)
    fees_per_member = models.IntegerField(default=0, blank=True)

    verification_required = models.BooleanField(blank=True, default=False)

    is_team_event = models.BooleanField(default=False)  #True for team based events
    min_team_size = models.SmallIntegerField(null=True, blank=True, default=None)
    max_team_size = models.SmallIntegerField(null=True, blank=True, default=None)

    rules_array = ArrayField(base_field=models.CharField(max_length=1000), null=True, default=None, blank=True)

    prize1 = models.CharField(max_length=150, null=True, blank=True, default=None)
    prize2 = models.CharField(max_length=150, null=True, blank=True, default=None)

    max_female_count = models.IntegerField(null=True, blank=True, default=None)
    max_male_count = models.IntegerField(null=True, blank=True, default=None)

    curr_male_count = models.IntegerField(blank=True, default=0)
    curr_female_count = models.IntegerField(blank=True, default=0)

    order = models.SmallIntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        cache.delete_many(['all', 'competitions', 'events'])
        super(Event, self).save(*args, **kwargs)

class Rule(models.Model):
    event = models.ForeignKey(Event, related_name='rules', on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    content = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.number)+'_'+self.event.name

# class Prize(models.Model):
#     event = models.ForeignKey(Event, related_name='prizes', on_delete=models.CASCADE)
#     position = models.CharField(max_length=50)
#     value = models.CharField(max_length=200)

#     def __str__(self):
#         return self.position+'_'+self.event.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leader_team_set')
    members = models.ManyToManyField(User, blank=True)
    max_count = models.IntegerField(default=1)
    amount_paid = models.BooleanField(default=False)
    is_thapar_team = models.BooleanField(default=True)
    def __str__(self):
        return self.name+'_'+self.event.name

class EventUserTable(models.Model):
    event = models.ForeignKey(Event, related_name='users', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='event_registrations', on_delete=models.CASCADE)
    amount_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email+'_'+self.event.name
