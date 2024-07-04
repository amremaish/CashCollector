from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Customer
from apps.core.permission import IsManager
from .serializers import UserSerializer, CustomerSerializer
from ..core.utils import Pagination, check_update_freeze_status


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        check_update_freeze_status(user)
        return Response({"is_frozen": user.is_frozen})


class AddCashCollector(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request):
        data = request.data
        data.update({
            'is_cash_collector': True,
            'is_manager': False,
            'is_staff': False,
            'is_superuser': False,
            'is_frozen': False
        })
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Cash Collector has been created"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpManager(APIView):
    permission_classes = [AllowAny]

    def put(self, request):
        data = request.data
        data.update({
            'is_cash_collector': False,
            'is_manager': True,
            'is_staff': True,
            'is_frozen': False
        })
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Successfully signed up as manager."}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request):
        data = request.data
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Customer created successfully.", "customer": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        paginator = Pagination()
        customers = Customer.objects.all().order_by('id')
        result_page = paginator.paginate_queryset(customers, request)
        serializer = CustomerSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
