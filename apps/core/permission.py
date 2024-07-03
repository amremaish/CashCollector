from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    """
    Custom permission to only allow access to users with is_manager = True.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_manager


class IsCashCollector(BasePermission):
    """
    Custom permission to only allow access to users with is_cash_collector = True.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_cash_collector
