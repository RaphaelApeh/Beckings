from django.conf import settings
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path, include
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from .feeds import ProductFeed


def health_check_view(request: HttpRequest) -> HttpResponse:
    
    return HttpResponse("Ok")


def homepage_view(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    
    _viewed = request.session.get("_viewed")
    if _viewed and request.user.is_authenticated:
        return redirect("/products/")
    if _viewed is None:
        request.session["_viewed"] = True
    return render(request, "landing/base.html")

urlpatterns = [
    path("", homepage_view, name="home"),
    path("admin/", admin.site.urls),
    path("products-rss/", ProductFeed()),
    path("health/", health_check_view, name="health-check"),
    path("products/", include("products.urls")),
    path("api/", include("api.urls"))
]

if settings.DEBUG:
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))
