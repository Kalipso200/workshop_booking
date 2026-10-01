"""Тесты мастер-классов."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Workshop

User = get_user_model()


class WorkshopAPITests(APITestCase):
    """Публичный доступ и права администратора."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="strongpass123",
            role=User.Role.ADMIN,
        )
        self.user = User.objects.create_user(
            username="user",
            password="strongpass123",
        )
        self.workshop = Workshop.objects.create(
            title="Django",
            date=timezone.now() + timedelta(days=1),
            capacity=10,
            created_by=self.admin,
        )

    def test_public_list(self):
        response = self.client.get(reverse("workshop-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_detail(self):
        response = self.client.get(
            reverse("workshop-detail", args=[self.workshop.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_create(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("workshop-list"), {
            "title": "X",
            "date": (timezone.now() + timedelta(days=2)).isoformat(),
            "capacity": 5,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse("workshop-list"), {
            "title": "X",
            "date": (timezone.now() + timedelta(days=2)).isoformat(),
            "capacity": 5,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_in_past(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse("workshop-list"), {
            "title": "Past",
            "date": (timezone.now() - timedelta(days=1)).isoformat(),
            "capacity": 5,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)