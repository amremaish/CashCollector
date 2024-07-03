from datetime import timedelta

from django.utils import timezone

from apps.tasks.models import Task
from apps.users.models import User


def check_freeze_status(cash_collector: User):
    if cash_collector.is_cash_collector:
        collected_amounts = Task.objects.filter(
            collected_by=cash_collector,
            collected_at__gte=timezone.now() - timedelta(days=2)
        )
        total_amount = sum([collection.amount for collection in collected_amounts])
        if total_amount >= 5000:
            cash_collector.is_frozen = True
            cash_collector.save()
