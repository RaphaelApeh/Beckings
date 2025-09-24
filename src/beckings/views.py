from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


def health_check_view(request: HttpRequest) -> HttpResponse:

    return HttpResponse("Ok")


def homepage_view(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:

    _viewed = request.session.get("_viewed")
    if _viewed or request.user.is_authenticated:
        return redirect("/products/")
    if _viewed is None:
        request.session["_viewed"] = True
    return render(request, "landing/base.html")


def robots_txt(request: HttpRequest) -> HttpResponse:

    sitemap = request.build_absolute_uri("/sitemap.xml")
    template = get_template("robots.txt")

    return HttpResponse("\n".join(template.render({"url": sitemap})))
