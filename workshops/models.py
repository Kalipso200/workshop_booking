"""Модели мастер-классов."""
from django.conf import settings
from django.db import models


class Workshop(models.Model):
    """Мастер-класс, на который можно записаться."""

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_workshops",
        verbose_name="Создатель",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("date",)
        verbose_name = "Мастер-класс"
        verbose_name_plural = "Мастер-классы"

    def __str__(self) -> str:
        return f"{self.title} ({self.date:%Y-%m-%d %H:%M})"

    @property
    def booked_seats(self) -> int:
        """Количество активных бронирований."""
        return self.bookings.filter(status="active").count()

    @property
    def available_seats(self) -> int:
        """Количество свободных мест."""
        return max(self.capacity - self.booked_seats, 0)