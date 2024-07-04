from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customer, User


class UserViewsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

        # Create users
        cls.manager = cls.create_user(
            username='manager',
            password='managerpass',
            email='manager@example.com',
            is_manager=True)

        cls.cash_collector = cls.create_user(
            username='cashcollector',
            password='cashcollectorpass',
            email='cashcollector@example.com',
            is_cash_collector=True)

        # Generate tokens
        cls.manager_token = cls.get_token_for_user(cls.manager)
        cls.cash_collector_token = cls.get_token_for_user(cls.cash_collector)

        # URLs
        cls.signup_manager_url = reverse('SignUpManager')
        cls.user_detail_url = reverse('user-detail')
        cls.user_status_url = reverse('user-status')
        cls.add_cash_collector_url = reverse('cash-collector')
        cls.customer_addition_url = reverse('CustomerAddition')
        cls.customer_listing_url = reverse('CustomerListing')

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

    def test_get_user_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "cashcollector")
        self.assertNotIn('password', response.data)

    def test_get_user_status(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        response = self.client.get(self.user_status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_frozen', response.data)

    def test_signup_manager(self):
        data = {
            'username': 'newmanager',
            'password': 'newmanagerpass',
            'email': 'newmanager@example.com',
            'first_name': 'New',
            'last_name': 'Manager'
        }

        response = self.client.put(self.signup_manager_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newmanager').exists())
        # send again to make sure it will raise an error
        response = self.client.put(self.signup_manager_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_cash_collector(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        data = {
            'username': 'newcollector',
            'password': 'newcollectorpass',
            'email': 'newcollector@example.com',
            'first_name': 'New',
            'last_name': 'Collector'
        }
        response = self.client.put(self.add_cash_collector_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newcollector').exists())

    def test_add_cash_collector_without_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        data = {
            'username': 'newcollector2',
            'password': 'newcollectorpass2',
            'email': 'newcollector2@example.com',
            'first_name': 'New2',
            'last_name': 'Collector2'
        }
        response = self.client.put(self.add_cash_collector_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_addition(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        data = {
            'name': 'Customer Test',
            'address': '1 Test St'
        }
        response = self.client.put(self.customer_addition_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Customer.objects.filter(name='Customer Test').exists())

    def test_customer_addition_without_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_token)
        data = {
            'name': 'Customer Test',
            'address': '1 Test St'
        }
        response = self.client.put(self.customer_addition_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        Customer.objects.create(name='Customer One', address='1 Test St')
        Customer.objects.create(name='Customer Two', address='1 Test St')
        response = self.client.get(self.customer_listing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['name'], 'Customer One')
        self.assertEqual(response.data['results'][1]['name'], 'Customer Two')
