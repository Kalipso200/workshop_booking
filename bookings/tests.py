"""Тесты бронирований."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from workshops.models import Workshop

User = get_user_model()


class BookingAPITests(APITestCase):
    """Создание, дубли, вместимость, изоляция броней."""

    def setUp(self):
        self.user = User.objects.create_user(username="u", password="strongpass123")
        self.other = User.objects.create_user(username="o", password="strongpass123")
        self.workshop = Workshop.objects.create(
            title="Test",
            date=timezone.now() + timedelta(days=1),
            capacity=1,
            created_by=self.user,
        )

    def test_requires_auth(self):
        response = self.client.post(
            reverse("booking-list"), {"workshop_id": self.workshop.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_booking(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("booking-list"), {"workshop_id": self.workshop.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("workshop", response.data)

    def test_duplicate_booking_forbidden(self):
        self.client.force_authenticate(self.user)
        self.client.post(reverse("booking-list"), {"workshop_id": self.workshop.id})
        response = self.client.post(
            reverse("booking-list"), {"workshop_id": self.workshop.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_capacity_limit(self):
        self.client.force_authenticate(self.user)
        self.client.post(reverse("booking-list"), {"workshop_id": self.workshop.id})
        self.client.force_authenticate(self.other)
        response = self.client.post(
            reverse("booking-list"), {"workshop_id": self.workshop.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_sees_only_own_bookings(self):
        self.client.force_authenticate(self.user)
        self.client.post(reverse("booking-list"), {"workshop_id": self.workshop.id})
        self.client.force_authenticate(self.other)
        response = self.client.get(reverse("booking-list"))
        self.assertEqual(response.data["count"], 0)

    def test_cancel_booking_changes_status(self):
        self.client.force_authenticate(self.user)
        create = self.client.post(
            reverse("booking-list"), {"workshop_id": self.workshop.id}
        )
        booking_id = create.data["id"]
        response = self.client.delete(
            reverse("booking-detail", args=[booking_id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # после отмены можно снова забронировать
        again = self.client.post(
            reverse("booking-list"), {"workshop_id": self.workshop.id}
        )
        self.assertEqual(again.status_code, status.HTTP_201_CREATED)