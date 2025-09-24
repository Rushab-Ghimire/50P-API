from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from authtf.models import (
    Customer,
    CustomerSerializer,
)

from business.models import Entity as Business

CUSTOMER_URL = reverse('authtf:customer-list')

def detail_url(_id):
    return reverse('authtf:customer-detail', args=[_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicCustomerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CUSTOMER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCustomerApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_customer(self):
        item = Customer.objects.create(
            user = self.user,
        )
        self.assertEqual(str(item.user.first_name), self.user.first_name)


    def test_all(self):
        Customer.objects.create(
            user = self.user,
            )
        Customer.objects.create(
            user = self.user,
            )

        res = self.client.get(CUSTOMER_URL)

        ccs = Customer.objects.all().order_by('-id')
        serializer = CustomerSerializer(ccs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_customer(self):
        item = Customer.objects.create(
            user = self.user,
            )

        payload = {'user': self.user.id}
        url = detail_url(item.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.user.id, payload['user'])

    def test_delete_customer(self):
        item = Customer.objects.create(
            user = self.user,
        )

        url = detail_url(item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertEqual(item.is_deleted, True)


    def test_add_customer_to_business(self):

        business = Business.objects.create(
            title = 'B1',
            description = 'B1 desc'
        )

        payload = {
            'business': [business.id],
        }
        res = self.client.post(CUSTOMER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
