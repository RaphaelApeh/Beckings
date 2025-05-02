from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.http import HttpRequest, HttpResponse


def health_check_view(request: HttpRequest) -> HttpResponse:
    
    return HttpResponse("Ok")


def comingsoon_view(request: HttpRequest) -> HttpRequest:

    return render(request, "landing/comingsoon.html")

urlpatterns = [
    path("", comingsoon_view, name="coming-soon"),
    path("admin/", admin.site.urls),
    path("health/", health_check_view, name="health-check"),
    path("products/", include("products.urls")),
    path("api/", include("api.urls"))
]

if settings.DEBUG:
    urlpatterns.insert(-1, path("__debug__/", include("debug_toolbar.urls")))
