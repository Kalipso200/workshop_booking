"""Маршруты приложения accounts."""
from django.urls import path
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ProfileView, RegisterView


@extend_schema(
    tags=["auth"],
    summary="Логин (получение JWT)",
    description="Возвращает пару токенов: `access` и `refresh`.",
    responses={
        200: OpenApiResponse(description="Токены успешно выданы"),
        401: OpenApiResponse(description="Неверные учётные данные"),
    },
    auth=[],
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    """POST /api/auth/login/ — вход и выдача JWT."""


@extend_schema(
    tags=["auth"],
    summary="Обновление access-токена",
    description="Принимает `refresh`, возвращает новый `access`.",
    responses={200: OpenApiResponse(description="Новый access-токен")},
    auth=[],
)
class DocumentedTokenRefreshView(TokenRefreshView):
    """POST /api/auth/refresh/ — обновление access-токена."""


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", DocumentedTokenObtainPairView.as_view(), name="login"),
    path("refresh/", DocumentedTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ProfileView.as_view(), name="me"),
]