"""Представления бронирований."""
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, permissions, viewsets

from .models import Booking
from .serializers import BookingSerializer
from .services import get_user_bookings


@extend_schema_view(
    list=extend_schema(
        tags=["bookings"],
        summary="Мои бронирования",
        description="Возвращает только брони текущего пользователя.",
    ),
    retrieve=extend_schema(
        tags=["bookings"],
        summary="Детали моей брони",
        description="Можно получить только свою бронь.",
    ),
    create=extend_schema(
        tags=["bookings"],
        summary="Создать бронь",
        description=(
            "Проверяет: дата в будущем, наличие свободных мест, "
            "отсутствие дублирующей активной брони."
        ),
        responses={
            201: BookingSerializer,
            400: OpenApiResponse(
                description="Нет мест / дубль / прошедшая дата"
            ),
        },
    ),
    destroy=extend_schema(
        tags=["bookings"],
        summary="Отменить бронь",
        description="Мягкая отмена: статус меняется на `cancelled`.",
        responses={204: OpenApiResponse(description="Бронь отменена")},
    ),
)
class BookingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Бронирования текущего пользователя.

    GET    /bookings/         — список своих броней
    POST   /bookings/         — создать бронь
    GET    /bookings/{id}/    — детали своей брони
    DELETE /bookings/{id}/    — отменить бронь (soft delete)
    """

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Только брони текущего пользователя."""
        return get_user_bookings(self.request.user)

    def perform_destroy(self, instance: Booking) -> None:
        """Мягкая отмена брони — меняем статус на cancelled."""
        instance.status = Booking.Status.CANCELLED
        instance.save(update_fields=["status"])