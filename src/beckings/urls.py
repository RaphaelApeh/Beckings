from django.contrib import admin
from django.urls import path, include

from .feeds import ProductFeed
from . import views


urlpatterns = [
    path("", views.homepage_view, name="home"),
    path("admin/", admin.site.urls),
    path("robots.txt", views.robots_txt),
    path("products-rss/", ProductFeed()),
    path("accounts/", include("clients.urls")),
    path("health/", views.health_check_view, name="health_check"),
    path("products/", include("products.urls")),
    path("api/", include("api.urls"))
]

