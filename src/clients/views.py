from typing import Any

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, resolve_url
from django.core.exceptions import ValidationError
from django.views.generic import (
    TemplateView, 
    FormView
)
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_variables
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout, login, REDIRECT_FIELD_NAME
from django.utils.translation import gettext_lazy as _

from .forms import (LoginForm, RegisterForm)


User = get_user_model()

never_cache_m = method_decorator(never_cache, name="dispatch")

class FormRequestMixin:

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs =  super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@never_cache_m
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
            messages.error(request, _("Authenticated User can register."))
            return HttpResponseRedirect(resolve_url("products"))
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Sign Up"
        return context

    def render_to_response(self, context, **response_kwargs):

        template_name = response_kwargs.pop("template_name", None)
        if template_name is not None:
            self.template_name = template_name
        
        assert self.template_name is not None
        return super().render_to_response(context, **response_kwargs)


    @method_decorator(sensitive_variables(["username", "password", "password1"]))
    def form_valid(self, form: RegisterForm) -> HttpResponse:
        self.object = obj = form.save()
        if getattr(settings, "USE_ACCOUNT_ACTIVATION_VIEW", True):
            form.send_email(self.request, obj)
            template_name = "accounts/check-email.html"
            return (
                self.render_to_response(self.get_context_data(), template_name=template_name)
            )
        messages.success(
            self.request,
            _("Account Created Sucessfully.")
        )
        return HttpResponseRedirect(resolve_url("login"))


class AccountActivationView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        
        user_id = kwargs.get("user_id")
        
        token = kwargs.get("token")

        if not all([user_id, token]):
            return self.handle_invalid_response()
        
        if self.check_token(request, user_id, token):
            user = self.get_user(user_id)
            redirect_url = resolve_url("login")
            
            if user.is_active:

                messages.info(request, _("Account already activated."))
                return HttpResponseRedirect(redirect_url)
            
            self.set_user_active_state(request, user)
            messages.success(request, _("Account Acctivated Successfully"))
            return HttpResponseRedirect(redirect_url)
        
        return self.handle_invalid_response()

    def check_token(self, request, user_id, token) -> bool:

        user = self.get_user(user_id)
        if user is None:
            return False
        return default_token_generator.check_token(user, token)

    def set_user_active_state(self, request, user) -> None:
        
        if request.user.is_authenticated:
            return
        assert not user.is_active

        user.is_active = True
        user.save()

    def get_user(self, user_id):

        try:
            pk = User._meta.pk.to_python(user_id)
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValidationError, ValueError, TypeError):
            user = None
        else:
            user = user
        return user

    def handle_invalid_response(self):
        raise Http404


class LogoutView(LoginRequiredMixin, TemplateView):

    """
    Logout page
    """
    template_name: str = "accounts/logout.html"
    
    def post(self, request: HttpRequest) -> HttpResponseRedirect:

        logout(request)

        messages.warning(request, "Loggedout Successfully.")
        return redirect("/accounts/login/")
    


class UserAccountView(LoginRequiredMixin, TemplateView):

    template_name = "accounts/overview.html"

