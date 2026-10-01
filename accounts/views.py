"""Представления аутентификации и профиля."""
from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import generics, permissions, status

from .serializers import UserRegisterSerializer, UserSerializer

User = get_user_model()


@extend_schema(
    tags=["auth"],
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя с ролью `user` по умолчанию.",
    request=UserRegisterSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description="Некорректные данные"),
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={
                "username": "ivan",
                "email": "ivan@example.com",
                "password": "strongpass123",
            },
            request_only=True,
        ),
    ],
    auth=[],
)
class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — регистрация нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=["auth"],
    summary="Текущий пользователь",
    description="Возвращает данные авторизованного пользователя.",
    responses={200: UserSerializer},
)
class ProfileView(generics.RetrieveAPIView):
    """GET /api/auth/me/ — информация о текущем пользователе."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user