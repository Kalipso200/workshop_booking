"""Сериализаторы бронирований."""
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from workshops.models import Workshop
from workshops.serializers import WorkshopSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    """Сериализатор брони с вложенным мастер-классом."""

    workshop = WorkshopSerializer(read_only=True)
    workshop_id = serializers.PrimaryKeyRelatedField(
        queryset=Workshop.objects.all(),
        source="workshop",
        write_only=True,
        help_text="ID мастер-класса, на который создаётся бронь",
    )

    class Meta:
        model = Booking
        fields = ("id", "workshop", "workshop_id", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")

    @extend_schema_field(WorkshopSerializer)
    def get_workshop(self, obj):
        """Хук для drf-spectacular: тип поля workshop — WorkshopSerializer."""
        return WorkshopSerializer(obj.workshop, context=self.context).data

    def validate_workshop_id(self, workshop: Workshop) -> Workshop:
        """
        Проверки при создании брони:
        - дата в будущем,
        - есть свободные места,
        - нет активной брони этого пользователя.
        """
        user = self.context["request"].user

        if workshop.date <= timezone.now():
            raise serializers.ValidationError(
                "Нельзя записаться на прошедший мастер-класс."
            )

        if workshop.available_seats <= 0:
            raise serializers.ValidationError("Нет свободных мест.")

        if Booking.objects.filter(
            user=user,
            workshop=workshop,
            status=Booking.Status.ACTIVE,
        ).exists():
            raise serializers.ValidationError(
                "Вы уже записаны на этот мастер-класс."
            )
        return workshop

    def create(self, validated_data):
        """Привязываем бронь к текущему пользователю."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)