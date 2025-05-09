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


