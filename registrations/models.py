from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager


import random
import string

# Create your models here.

def uploadPath(instance, filename):
    return f"id/{instance.name}_{''.join(random.choice(string.ascii_letters) for _ in range(5))}_{filename}"

#to do :-
#primary keys of phone number and roll number
class User(AbstractBaseUser):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone_no = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, null=True, blank=True, default=None, choices=GENDER_CHOICES)

    is_thaparian = models.BooleanField(blank=True, default=False)
    roll_no = models.CharField(max_length=15, null=True, blank=True, default=None)

    id_proof = models.URLField(max_length=5000, null=True, blank=True, default=None)
    college = models.CharField(max_length=350, null=True, blank=True, default=None)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    otp = models.CharField(max_length=7, null=True, blank=True, default=None)

    def get_short_name(self):
        # The user is identified by their email
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    def __str__(self):
        return self.email

# class EmailVerification(models.Model):
#     # otp = models.CharField(max_length=10)
#     slug = models.CharField(max_length=50)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.user.email

class UnverifiedUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone_no = models.CharField(max_length=15)
    gender = models.CharField(max_length=20, null=True, default=None)

    is_thaparian = models.BooleanField(blank=True, default=False)
    roll_no = models.CharField(max_length=15, null=True, blank=True, default=None)

    id_proof = models.URLField(max_length=5000, null=True, blank=True, default=None)
    college = models.CharField(max_length=350, null=True, blank=True, default=None)
    slug = models.CharField(max_length=50)
    
    password = models.CharField(max_length=150)

    def __str__(self):
        return self.email

class PendingEmail(models.Model):
    email = models.EmailField()

    is_main = models.BooleanField(default=False)
    slug = models.CharField(max_length=50, default='', blank=True)
    main_vrf_skip = models.BooleanField(default=False)

    is_event = models.BooleanField(default=False)
    event = models.CharField(max_length=150, default='', blank=True)
    individual_fees = models.IntegerField(default=0)

    fees_required = models.BooleanField(default=False)

    is_create_team = models.BooleanField(default=False)
    team_name = models.CharField(max_length=150, default='', blank=True)
    team_key = models.CharField(max_length=20, default='', blank=True)
    team_amount = models.IntegerField(default=0)
    members_count = models.IntegerField(default=0)
    fees_per_member = models.IntegerField(default=0)
    ignore_message = models.BooleanField(default=False)

    is_join_team = models.BooleanField(default=False)

    qr_url = models.URLField(max_length=200, null=True, default=None, blank=True)

    def __str__(self):
        return self.email
