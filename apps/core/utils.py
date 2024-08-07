from rest_framework.pagination import PageNumberPagination
from datetime import timedelta
from django.utils import timezone
from CashCollector import settings
from apps.tasks.models import Task
from apps.users.models import User


class Pagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Optional: limit the maximum page size


def check_update_freeze_status(cash_collector: User):
    if cash_collector.is_frozen:
        return True

    if cash_collector.is_cash_collector:
        collected_amounts = Task.objects.filter(
            assigned_to=cash_collector,
            collected_at__lte=timezone.now() - timedelta(days=settings.THRESHOLD_DAYS),
            delivered_to_manager_at=None
        )
        total_amount = sum([task.amount_due for task in collected_amounts if task.amount_due])
        if total_amount >= settings.MAX_CASH_THRESHOLD:
            cash_collector.is_frozen = True
            cash_collector.save()
            return True
    return False
