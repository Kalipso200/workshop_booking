"""Сервисный слой для мастер-классов."""
from django.db.models import QuerySet

from .models import Workshop


def get_workshops_queryset() -> QuerySet[Workshop]:
    """Оптимизированный queryset мастер-классов (борьба с N+1)."""
    return (
        Workshop.objects
        .select_related("created_by")
        .prefetch_related("bookings")
    )