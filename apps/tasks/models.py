from django.db import models

from apps.core.models import TimeStampedModel
from apps.users.models import User, Customer


class Task(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount_due = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_to_manager_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
