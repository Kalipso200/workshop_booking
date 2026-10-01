"""Маршруты приложения workshops."""
from rest_framework.routers import DefaultRouter

from .views import WorkshopViewSet

router = DefaultRouter()
router.register(r"workshops", WorkshopViewSet, basename="workshop")

urlpatterns = router.urls