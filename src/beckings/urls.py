from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.http import HttpRequest, HttpResponse


def health_check_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Ok")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check_view, name="health-check"),
]

if settings.DEBUG:
    urlpatterns.insert(-1, path("__debug__/", include("debug_toolbar.urls")))
