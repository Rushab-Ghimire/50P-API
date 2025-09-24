from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from business.models import (
    Entity as Business,
    BusinessSerializer
)

BUSINESS_URL = reverse('business:entity-list')

def detail_url(_id):
    return reverse('business:entity-detail', args=[_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicBusinessApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BUSINESS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBusinessApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_business(self):
        item = Business.objects.create(
            user=self.user,
            title='B1',
            description='B1 description.',
        )
        self.assertEqual(str(item.title), item.title)


    def test_all(self):
        Business.objects.create(
            user = self.user,
            title = 'B1',
            description = 'B1 desc'
            )
        Business.objects.create(
            user = self.user,
            title = 'B2',
            description = 'B2 desc'
            )

        res = self.client.get(BUSINESS_URL)

        ccs = Business.objects.all().order_by('-title')
        serializer = BusinessSerializer(ccs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_business(self):
        item = Business.objects.create(
            user = self.user,
            title = 'B3',
            description = 'B3 desc'
        )

        payload = {'title': 'B4'}
        url = detail_url(item.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.title, payload['title'])

    def test_delete_business(self):
        item = Business.objects.create(
            user = self.user,
            title = 'B5',
            description = 'B5 desc'
        )

        url = detail_url(item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertEqual(item.is_deleted, True)
