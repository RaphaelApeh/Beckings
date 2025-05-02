from django.urls import path #noqa
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = []


router = DefaultRouter()

router.register("users", views.UserAPIView)

urlpatterns += router.urls

