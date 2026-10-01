"""Модели бронирований."""
from django.conf import settings
from django.db import models

from workshops.models import Workshop


class Booking(models.Model):
    """Бронирование места на мастер-классе."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Активно"
        CANCELLED = "cancelled", "Отменено"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Мастер-класс",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        constraints = [
            # Запрет дублирования активной брони пользователя
            # на один и тот же мастер-класс.
            models.UniqueConstraint(
                fields=("user", "workshop"),
                condition=models.Q(status="active"),
                name="unique_active_booking_per_user_workshop",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.workshop} [{self.status}]"