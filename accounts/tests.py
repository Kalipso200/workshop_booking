"""Тесты приложения accounts."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    """Регистрация, логин, профиль."""

    def test_register_user(self):
        response = self.client.post(reverse("register"), {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpass123",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

    def test_login_returns_tokens(self):
        User.objects.create_user(username="u1", password="strongpass123")
        response = self.client.post(reverse("login"), {
            "username": "u1",
            "password": "strongpass123",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_requires_auth(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_current_user(self):
        user = User.objects.create_user(username="u2", password="strongpass123")
        self.client.force_authenticate(user)
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "u2")