"""Админка бронирований."""
from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Настройки отображения Booking в админке."""

    list_display = ("id", "user", "workshop", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "workshop__title")
    autocomplete_fields = ("workshop",)