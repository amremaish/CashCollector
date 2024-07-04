from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from apps.core.admin_filters import CompletedFilter, AssignedFilter
from apps.tasks.models import Task
from apps.users.models import CashCollector, Manager

# Unregister Group models
admin.site.unregister(Group)


class CashCollectorAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_cash_collector')
    list_filter = ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_cash_collector=True)


class ManagerAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_manager')
    list_filter = ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_manager=True)


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'amount_due', 'assigned_to', 'collected_at', 'delivered_to_manager_at', 'completed')
    list_filter = (CompletedFilter, AssignedFilter, 'assigned_to')
    search_fields = ('customer__name', 'assigned_to__username')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:  # When adding a new task
            return [field.name for field in self.model._meta.fields if field.name != 'customer']
        return super().get_readonly_fields(request, obj)


admin.site.register(Task, TaskAdmin)
admin.site.register(CashCollector, CashCollectorAdmin)
admin.site.register(Manager, ManagerAdmin)
