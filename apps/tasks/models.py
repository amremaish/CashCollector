from django.db import models
from apps.users.models import User


class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)


class Task(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_to_manager_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
