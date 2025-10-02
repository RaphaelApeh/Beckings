from django.urls import path

from .views import FeedBackCreateView

urlpatterns = [
    path("", FeedBackCreateView.as_view())
]