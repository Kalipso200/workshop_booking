"""Админка мастер-классов."""
from django.contrib import admin

from .models import Workshop


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    """Настройки отображения Workshop в админке."""

    list_display = ("id", "title", "date", "capacity", "created_by", "created_at")
    search_fields = ("title", "description")
    list_filter = ("date",)
    ordering = ("-date",)