from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UserAPIView,
    ProductViewSet,
    TokenLoginAPIView
    )


urlpatterns = [
    path("login/", TokenLoginAPIView.as_view(), name="api_login")
]


router = DefaultRouter()

router.register("users", UserAPIView)
router.register("products", ProductViewSet)

urlpatterns += router.urls

