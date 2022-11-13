from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager

import random
import string

# Create your models here.

def uploadPath(instance, filename):
    return f"id/{instance.name}_{''.join(random.choice(string.ascii_letters) for _ in range(5))}_{filename}"

class User(AbstractBaseUser):
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone_no = models.CharField(max_length=15, unique=True)

    is_thaparian = models.BooleanField(blank=True, default=False)
    roll_no = models.CharField(max_length=15, null=True, blank=True, default=None, unique=True)

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

class EmailVerification(models.Model):
    # otp = models.CharField(max_length=10)
    slug = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user
