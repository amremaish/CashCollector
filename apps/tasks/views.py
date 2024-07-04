import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permission import IsCashCollector, IsManager
from apps.core.utils import Pagination, check_update_freeze_status
from apps.tasks.serializer import *


class TaskLisTView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        paginator = Pagination()

        if user.is_manager:
            tasks = Task.objects.all().order_by('-id')
        elif user.is_cash_collector:
            tasks = Task.objects.filter(assigned_to=user, completed=True).order_by('-id')
        else:
            tasks = Task.objects.none()

        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request):
        serializer = TaskCreationSerializer(data=request.data)
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
            return Response({"detail": "Your account is frozen, please deliver the cash"},
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
        task.save()
        serializer = TaskSerializer(task)
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


class GenerateTasksCSV(APIView):
    permission_classes = [IsAuthenticated, IsManager | IsCashCollector]

    def get(self, request, *args, **kwargs):
        # Parse and validate query parameters
        filter_serializer = TaskFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ['ID', 'Customer', 'Amount Due', 'Assigned To', 'Collected At', 'Delivered To Manager At', 'Completed',
             'Created At', 'Modified At'])

        tasks = self.get_filtered_tasks(filters, request.user)
        self.write_tasks_to_csv(writer, tasks)

        return response

    def get_filtered_tasks(self, filters, user):

        if user.is_cash_collector:
            tasks = Task.objects.filter(assigned_to=user)
        else:
            tasks = Task.objects.all()

        if filters.get('completed'):
            tasks = tasks.filter(completed=filters['completed'])

        if filters.get('assigned'):
            tasks = tasks.filter(assigned_to__isnull=not filters['assigned'])

        if filters.get('delivered'):
            tasks = tasks.filter(delivered_to_manager_at__isnull=not filters['delivered'])

        return tasks

    def write_tasks_to_csv(self, writer, tasks):
        for task in tasks:
            writer.writerow([
                task.id,
                task.customer.name,
                task.amount_due,
                task.assigned_to.username if task.assigned_to else '',
                task.collected_at,
                task.delivered_to_manager_at,
                task.completed,
                task.created_at,
                task.modified_at,
            ])
