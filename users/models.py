from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(max_length=255, blank=False, unique=True)
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'