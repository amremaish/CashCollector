from rest_framework import serializers

from apps.tasks.models import Task
from apps.users.models import Customer


class CustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)


class TaskCreationSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())


class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(read_only=True)
    collected_at = serializers.DateTimeField(read_only=True, allow_null=True, required=False)
    delivered_to_manager_at = serializers.DateTimeField(read_only=True, allow_null=True, required=False)
    completed = serializers.BooleanField(default=False, read_only=True)
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def create(self, validated_data):
        return Task.objects.create(**validated_data)


class TaskCashCollectorSerializer(serializers.Serializer):
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2)


class TaskFilterSerializer(serializers.Serializer):
    completed = serializers.BooleanField(required=False)
    assigned = serializers.BooleanField(required=False)
    delivered = serializers.BooleanField(required=False)
