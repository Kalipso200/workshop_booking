"""Кастомные разрешения для DRF."""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Разрешает доступ только пользователям с ролью admin (или суперюзерам)."""

    message = "Доступ только для администраторов."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_admin", False)
        )