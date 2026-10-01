"""Сервисный слой бронирований."""
from django.db.models import QuerySet

from .models import Booking


def get_user_bookings(user) -> QuerySet[Booking]:
    """Активные брони пользователя с оптимизацией выборки (N+1)."""
    return (
        Booking.objects
        .filter(user=user)
        .select_related("workshop", "workshop__created_by")
        .order_by("-created_at")
    )