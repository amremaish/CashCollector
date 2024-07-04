from django.urls import path
from .views import *

urlpatterns = [
    path('add', TaskListCreateView.as_view(), name='task-list-create'),
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('next_task', NextTaskView.as_view(), name='next-task'),
    path('<int:pk>/collect', TaskCollectView.as_view(), name='task-collect'),
    path('<int:pk>/deliver', TaskDeliverView.as_view(), name='task-deliver'),
]