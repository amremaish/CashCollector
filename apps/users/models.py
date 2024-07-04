from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    is_cash_collector = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)


class Customer(TimeStampedModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - {self.name}"


class CashCollector(User):
    class Meta:
        proxy = True
        verbose_name = 'Cash Collector'
        verbose_name_plural = 'Cash Collectors'


class Manager(User):
    class Meta:
        proxy = True
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'
