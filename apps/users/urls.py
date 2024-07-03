from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.views import *

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetail.as_view(), name='user-detail'),
    path('status/', UserStatus.as_view(), name='user-status'),
    path('add/cash-collector', AddCashCollector.as_view(), name='cash-collector'),
    path('manager/signup', SignUpManager.as_view(), name='manager'),
]
