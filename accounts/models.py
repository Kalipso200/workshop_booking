"""Модель пользователя с ролями."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомный пользователь с ролью (admin/user)."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        USER = "user", "Пользователь"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="Роль",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_admin(self) -> bool:
        """True, если пользователь — администратор (или суперюзер)."""
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"