from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_cash_collector = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)


class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)