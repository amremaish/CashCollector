from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from CashCollector import settings
from apps.users.models import User, Customer
from apps.tasks.models import Task


class TaskViewsTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        # Create users
        cls.manager = cls.create_user(username='manager', password='managerpass', email='manager@example.com',
                                      is_manager=True)
        cls.cash_collector = cls.create_user(username='cashcollector', password='cashcollectorpass',
                                             email='cashcollector@example.com', is_cash_collector=True)

        # Generate tokens
        cls.manager_token = cls.get_token_for_user(cls.manager)
        cls.cash_collector_token = cls.get_token_for_user(cls.cash_collector)

        # Create customers
        cls.customer = Customer.objects.create(name='Customer One', address='123 Main St')

        # URLs
        cls.task_create = reverse('task-create')
        cls.task_list = reverse('task-list')
        cls.next_task_url = reverse('next-task')
        cls.generate_tasks_csv_url = reverse('generate-tasks-csv')

    @classmethod
    def create_user(cls, username, password, email, **extra_fields):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            **extra_fields
        )
        return user

    @classmethod
    def get_token_for_user(cls, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_get_tasks_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.get(self.task_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        data = {
            'customer': self.customer.id
        }
        response = self.client.put(self.task_create, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_without_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        data = {
            'customer': self.customer.id
        }
        response = self.client.put(self.task_create, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_next_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        Task.objects.create(customer=self.customer)
        response = self.client.get(self.next_task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assigned_to'], self.cash_collector.id)

    def test_collect_task(self):
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        response = self.client.post(url, {'amount_due': '100.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.assigned_to.id, self.cash_collector.id)

    def test_collect_task_assigned_to_another_user(self):
        another_user = self.create_user(username='anotheruser', password='anotherpass', email='anotheruser@example.com')
        task = Task.objects.create(customer=self.customer, assigned_to=another_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        data = {'amount_due': '100.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You cannot collect this task.')

    def test_collect_task_already_collected(self):
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector, collected_at=timezone.now())
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        data = {'amount_due': '100.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'This task is collected before.')

    def test_collect_task_already_completed(self):
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector, completed=True)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        data = {'amount_due': '100.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'This task is already completed.')

    def test_collect_task_invalid_data(self):
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        data = {'amount_due': 'invalid'}  # Invalid data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_deliver_task(self):
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector, collected_at=timezone.now())
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        url = reverse('task-deliver', kwargs={'pk': task.pk})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertIsNotNone(task.delivered_to_manager_at)
        self.assertTrue(task.completed)

    def test_generate_tasks_csv(self):
        Task.objects.create(customer=self.customer, assigned_to=self.cash_collector, collected_at=timezone.now(),
                            delivered_to_manager_at=timezone.now(), completed=True)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.get(self.generate_tasks_csv_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="tasks.csv"', response['Content-Disposition'])

    def test_freeze_account_not_yet_due(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        Task.objects.create(customer=self.customer, assigned_to=self.cash_collector, amount_due=6000.00,
                            collected_at=timezone.now() - timedelta(days=1, hours=23))
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector, amount_due=4000.00)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        data = {'amount_due': '4000.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.assigned_to.id, self.cash_collector.id)

    def test_freeze_account(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        Task.objects.create(
            customer=self.customer,
            assigned_to=self.cash_collector,
            amount_due=settings.MAX_CASH_THRESHOLD,
            collected_at=timezone.now() - timedelta(days=settings.THRESHOLD_DAYS + 1)
        )
        task = Task.objects.create(customer=self.customer, assigned_to=self.cash_collector)
        url = reverse('task-collect', kwargs={'pk': task.pk})
        data = {'amount_due': '4000.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Your account is frozen, please deliver the cash')