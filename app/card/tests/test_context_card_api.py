from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from card.models import (
    ContextCard,
    ContextCardSerializer
)

CONTEXT_CARD_URL = reverse('card:contextcard-list')

def detail_url(cc_id):
    """Create and return a tag detail url."""
    return reverse('card:contextcard-detail', args=[cc_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicContextCardApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(CONTEXT_CARD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateContextCardApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_create_context_card(self):
        card = ContextCard.objects.create(
            user=self.user,
            title='Context Cards',
            context='context-card-1',
            description='Sample Card description.',
        )
        self.assertEqual(str(card.title), card.title)


    def test_all(self):
        """Test retrieving a list of tags."""
        ContextCard.objects.create(
            user = self.user,
            title = 'T1',
            context = 't1',
            description = 'T1 desc'
            )
        ContextCard.objects.create(
            user = self.user,
            title = 'T2',
            context = 't2',
            description = 'T2 desc'
            )

        res = self.client.get(CONTEXT_CARD_URL)

        ccs = ContextCard.objects.all().order_by('-title')
        serializer = ContextCardSerializer(ccs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_context_card(self):
        """Test updating a context_card."""
        cc = ContextCard.objects.create(
            user = self.user,
            title = 'T2',
            context = 't2',
            description = 'T2 desc'
        )

        payload = {'title': 'T3'}
        url = detail_url(cc.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cc.refresh_from_db()
        self.assertEqual(cc.title, payload['title'])

    def test_delete_context_card(self):
        """Test deleting a context_card."""
        cc = ContextCard.objects.create(
            user = self.user,
            title = 'T2',
            context = 't2',
            description = 'T2 desc'
        )

        url = detail_url(cc.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        cc.refresh_from_db()
        self.assertEqual(cc.is_deleted, True)
