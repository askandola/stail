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

    is_thaparian = models.BooleanField(blank=True, default=False)
    roll_no = models.CharField(max_length=15, null=True, blank=True, default=None)

    id_proof = models.ImageField(upload_to=uploadPath, null=True, blank=True, default=None)

    college = models.CharField(max_length=350, null=True, blank=True, default=None)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    # otp = models.CharField(max_length=6, null=True, blank=True, default=None)
    # tries = models.IntegerField(default=0)
    
    # def save(self, *args, **kwargs):
    #     number_list = [x for x in range(10)]  # Use of list comprehension
    #     code_items_for_otp = []

    #     for i in range(6):
    #         num = random.choice(number_list)
    #         code_items_for_otp.append(num)

    #     code_string = "".join(str(item) for item in code_items_for_otp)  # list comprehension again
    #     # A six digit random number from the list will be saved in top field
    #     self.otp = code_string
    #     super().save(*args, **kwargs)
        

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
