"""Представления мастер-классов (CRUD)."""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from accounts.permissions import IsAdminRole

from .serializers import WorkshopSerializer
from .services import get_workshops_queryset


@extend_schema_view(
    list=extend_schema(
        tags=["workshops"],
        summary="Список мастер-классов",
        description="Публичный просмотр. Доступно без авторизации.",
    ),
    retrieve=extend_schema(
        tags=["workshops"],
        summary="Детали мастер-класса",
        description="Публичный просмотр. Доступно без авторизации.",
    ),
    create=extend_schema(
        tags=["workshops"],
        summary="Создать мастер-класс",
        description="Доступно только пользователям с ролью `admin`.",
    ),
    update=extend_schema(
        tags=["workshops"],
        summary="Обновить мастер-класс (полностью)",
        description="Доступно только пользователям с ролью `admin`.",
    ),
    partial_update=extend_schema(
        tags=["workshops"],
        summary="Обновить мастер-класс (частично)",
        description="Доступно только пользователям с ролью `admin`.",
    ),
    destroy=extend_schema(
        tags=["workshops"],
        summary="Удалить мастер-класс",
        description="Доступно только пользователям с ролью `admin`.",
    ),
)
class WorkshopViewSet(viewsets.ModelViewSet):
    """
    ViewSet мастер-классов.

    GET — доступно всем (публичный просмотр).
    POST/PUT/PATCH/DELETE — только администратору.
    """

    serializer_class = WorkshopSerializer

    def get_queryset(self):
        """Оптимизированный queryset (select_related / prefetch_related)."""
        return get_workshops_queryset()

    def get_permissions(self):
        """Публичное чтение, изменение — только админ."""
        if self.action in ("list", "retrieve"):
            return super().get_permissions()
        return [IsAdminRole()]

    def perform_create(self, serializer):
        """Сохраняем автора мастер-класса."""
        serializer.save(created_by=self.request.user)