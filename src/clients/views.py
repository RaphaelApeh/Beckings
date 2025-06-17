from typing import Any

from django.contrib import messages
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.generic import View, FormView
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth import logout, login, authenticate, REDIRECT_FIELD_NAME

from .forms import (LoginForm, RegisterForm)



class FormRequestMixin:

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs =  super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class LoginView(FormRequestMixin, FormView):

    template_name = "accounts/auth.html"
    success_url = "/products/"
    form_class = LoginForm

    
    def dispatch(self, request, *args: list[str], **kwargs: dict[str, str]) -> HttpResponse:
        if request.user.is_authenticated:
            messages.error(request, "Authenticated User can re-login.")
            _url = request.META["HTTP_RERFER"] or "/products/"
            return redirect(_url)
        self.next_url = request.GET.get(REDIRECT_FIELD_NAME)
        return super().dispatch(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Login"
        return context
    

    def form_valid(self, form: LoginForm) -> HttpResponseRedirect:
        request = self.request
        user = form.get_user()
        if user is None:
            messages.error(request, "Something went wrong :(")
            return redirect("register")
        login(request, user)
        messages.success(request, "Loggedin Successfully :)")
        next_url = self.next_url or self.success_url
        return redirect(next_url)
    

    def validate_path(self, path: str) -> None:
        
        if path.startswith(("https", "http")):...


class RegisterView(FormView):

    template_name = "accounts/auth.html"
    form_class = RegisterForm

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            messages.error(request, "Authenticated User can register.")
            return redirect("/products/")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Sign Up"
        return context

    @method_decorator(sensitive_variables(["username", "password", "password1"]))
    def form_valid(self, form: RegisterForm) -> HttpResponseRedirect:
        data = form.cleaned_data
        form.save()
        username = data["username"]
        password = data["password1"]
        if not all([username, password]):
            return HttpResponseBadRequest()
        user = authenticate(self.request, username=username, password=password)
        if user is None:
            messages.error(self.request, "Something went Wrong.")
            return redirect("login") # return to the login page
        messages.success(self.request, "Account created Successfully.")
        login(self.request, user)
        return redirect("products")


class LogoutView(View):

    """
    Logout page
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_anonymous:
            messages.warning(request, "Something went wrong :(")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:

        return render(request, "accounts/logout.html")
    
    def post(self, request: HttpRequest) -> HttpResponseRedirect:

        logout(request)
        messages.warning(request, "Loggedout Successfully.")
        return redirect("/accounts/login/")
    

