from rest_framework import serializers

from apps.tasks.models import Task


class CustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)


class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    customer = CustomerSerializer(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(read_only=True)
    collected_at = serializers.DateTimeField(read_only=True, allow_null=True, required=False)
    delivered_to_manager_at = serializers.DateTimeField(read_only=True, allow_null=True, required=False)
    completed = serializers.BooleanField(default=False, read_only=True)
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def create(self, validated_data):
        return Task.objects.create(**validated_data)


class TaskCashCollectorSerializer(serializers.Serializer):
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2)