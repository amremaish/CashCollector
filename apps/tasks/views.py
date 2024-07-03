from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permission import IsCashCollector
from apps.core.utils import Pagination, check_update_freeze_status
from apps.tasks.models import Task
from apps.tasks.serializer import TaskSerializer, TaskCashCollectorSerializer


class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        paginator = Pagination()

        if user.is_manager:
            tasks = Task.objects.all()
        elif user.is_cash_collector:
            tasks = Task.objects.filter(assigned_to=user)
        else:
            tasks = Task.objects.none()

        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def put(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NextTaskView(APIView):
    permission_classes = [IsAuthenticated, IsCashCollector]

    def get(self, request):
        next_task = Task.objects.filter(assigned_to__isnull=True).first()
        if not next_task:
            return Response({"detail": "No tasks available."}, status=status.HTTP_404_NOT_FOUND)

        if check_update_freeze_status(request.user):
            return Response({"detail": "You account is frozen, You can't receive tasks"},
                            status=status.HTTP_403_FORBIDDEN)

        # set task for the current cash collector
        next_task.assigned_to = request.user
        next_task.save()
        serializer = TaskSerializer(next_task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCollectView(APIView):
    permission_classes = [IsAuthenticated, IsCashCollector]

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        cash_serializer = TaskCashCollectorSerializer(data=request.data)
        # Ensure the task is assigned to the current user if not already done
        if task.assigned_to and task.assigned_to != request.user:
            return Response({"detail": "You cannot collect this task."}, status=status.HTTP_403_FORBIDDEN)

        if check_update_freeze_status(request.user):
            return Response({"detail": "You account is frozen, please deliver the cash"},
                            status=status.HTTP_403_FORBIDDEN)

        if task.collected_at:
            return Response({"detail": "This task is collected before."}, status=status.HTTP_403_FORBIDDEN)

        if task.completed:
            return Response({"detail": "This task is already completed."}, status=status.HTTP_403_FORBIDDEN)

        if not cash_serializer.is_valid():
            return Response({"detail": cash_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Update collected_at
        task.collected_at = timezone.now()
        task.amount_due = cash_serializer.validated_data['amount_due']

        serializer = TaskSerializer(task, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task.save()

        return Response(serializer.data)


class TaskDeliverView(APIView):
    permission_classes = [IsAuthenticated, IsCashCollector]

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.completed:
            return Response({"detail": "This task is already completed."}, status=status.HTTP_403_FORBIDDEN)

        task.delivered_to_manager_at = timezone.now()
        task.completed = True
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data)
