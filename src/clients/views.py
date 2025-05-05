from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from django.views.generic import View, FormView
from django.contrib.auth import logout, login, authenticate

from .forms import (LoginForm, RegisterForm)


class LoginView(FormView):

    template_name = "accounts/auth.html"
    success_url = "/products/"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/products/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Login"
        return context
    

    def form_valid(self, form):
        data = form.cleaned_data
        request = self.request
        _login = data["login"]
        password = data["password"]
        user = authenticate(request, username=_login, password=password)
        if user is None:
            messages.error(request, "Invalid credentials :(")
            return redirect("login") # refresh
        login(request, user)
        messages.success(request, "Login Successfully :)")
        return redirect(self.success_url)
    

class RegisterView(FormView):

    template_name = "accounts/auth.html"
    form_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/products/")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Sign Up"
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        form.save()
        username = data["username"]
        password = data["password1"]
        if not all([username, password]):
            return HttpResponseBadRequest()
        user = authenticate(self.request, username=username, password=password)
        if user is None:
            return redirect("login") # return to the login page
        login(self.request, user)
        return redirect("product-list")


class LogoutView(View):

    """
    Logout page
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        return render(request, "accounts/logout.html")
    
    def post(self, request):

        logout(request)

        return redirect("/accounts/login/")
    

