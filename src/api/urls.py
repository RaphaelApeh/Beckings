from django.urls import path #noqa
from rest_framework.routers import DefaultRouter

from .views import (
    UserAPIView,
    ProductViewSet)


urlpatterns = []


router = DefaultRouter()

router.register("users", UserAPIView)
router.register("products", ProductViewSet)

urlpatterns += router.urls

