from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from business.models import (
    Task, Entity as Business,
    TaskSerializer
)

TASK_URL = reverse('business:task-list')

def detail_url(_id):
    return reverse('business:task-detail', args=[_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_business(title='B1', description='B1 desc', user = {}):
    return Business.objects.create(
            user = user,
            title = title,
            description = description
            )


class PublicTaskApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTaskApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.business = create_business(user = self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_task(self):
        item = Task.objects.create(
            user = self.user,
            business = self.business,
            title = 'T1',
            description = 'T1 description.',
        )
        self.assertEqual(str(item.title), item.title)


    def test_all(self):
        Task.objects.create(
            user = self.user,
            business = self.business,
            title = 'T1',
            description = 'T1 description.',
            )
        Task.objects.create(
            user = self.user,
            business = self.business,
            title = 'T2',
            description = 'T2 description.',
            )

        res = self.client.get(TASK_URL)

        ccs = Task.objects.all().order_by('-title')
        serializer = TaskSerializer(ccs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_task(self):
        item = Task.objects.create(
            user = self.user,
            business = self.business,
            title = 'T3',
            description = 'T3 description.',
            )

        payload = {'title': 'T4'}
        url = detail_url(item.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.title, payload['title'])

    def test_delete_task(self):
        item = Task.objects.create(
            user = self.user,
            business = self.business,
            title = 'T5',
            description = 'T5 description.',
        )

        url = detail_url(item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertEqual(item.is_deleted, True)
