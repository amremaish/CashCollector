from django.contrib import admin


class CompletedFilter(admin.SimpleListFilter):
    title = 'Completed status'
    parameter_name = 'completed'

    def lookups(self, request, model_admin):
        return [
            ('completed', 'Completed'),
            ('not_completed', 'Not Completed'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'completed':
            return queryset.filter(completed=True)
        elif self.value() == 'not_completed':
            return queryset.filter(completed=False)
        return queryset


class AssignedFilter(admin.SimpleListFilter):
    title = 'Assignment status'
    parameter_name = 'assigned_to'

    def lookups(self, request, model_admin):
        return [
            ('assigned', 'Assigned'),
            ('not_assigned', 'Not Assigned'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'assigned':
            return queryset.filter(assigned_to__isnull=False)
        elif self.value() == 'not_assigned':
            return queryset.filter(assigned_to__isnull=True)
        return queryset
