"""Сериализаторы мастер-классов."""
from django.utils import timezone
from rest_framework import serializers

from .models import Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    """Сериализатор мастер-класса (чтение/запись)."""

    booked_seats = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workshop
        fields = (
            "id",
            "title",
            "description",
            "date",
            "capacity",
            "booked_seats",
            "available_seats",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "booked_seats",
            "available_seats",
        )

    def validate_date(self, value):
        """Запрет создания мастер-класса в прошлом."""
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Нельзя создать мастер-класс в прошлом."
            )
        return value

    def validate_capacity(self, value):
        """Вместимость должна быть положительной."""
        if value <= 0:
            raise serializers.ValidationError(
                "Вместимость должна быть положительной."
            )
        return value