from functools import partial

from django import forms
from django.core import mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import get_template
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import (
    PHONE_NUMBER_REGEX,
    NIGERIA_PHONE_NUMBER,
    Client
)

User = get_user_model()


class PasswordField(forms.CharField):

    widget = forms.PasswordInput


class LoginForm(forms.Form):

    login = forms.CharField(label="Username or Email", required=True, widget=forms.TextInput({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"}))

    password = PasswordField(widget=forms.PasswordInput({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"}))

    def __init__(self, *args, **kwargs) -> None:
        request = kwargs.pop("request", None)
        self._user = None
        self.init_request(request)
        
        super().__init__(*args, **kwargs)
        
        if not hasattr(self, "request"):
            raise AttributeError(f"{self.__class__.__name__} has not attribute request.")

    
    def init_request(self, request) -> None:

        if request is not None:
            self.request = request
        
        return None
    
    def get_user(self):
        
        return self._user

    def clean(self):
        login = self.cleaned_data.get("login")
        password = self.cleaned_data.get("password")
        user = authenticate(self.request, username=login, password=password)
        if user is None:
            self.add_error(None, "Invaild credentials :(")
        self._user = user
        return super().clean()


class RegisterForm(UserCreationForm):

    phone_number = forms.RegexField(
        regex=PHONE_NUMBER_REGEX,
        widget=forms.TelInput({
            "pattern": PHONE_NUMBER_REGEX,
            "title": "Enter a valid phone number e.g(+2348139582053)"
        })
    )
        
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = ""
            self.fields[field].widget.attrs.update({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"})

    
    def clean(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            self.add_error("email", "Email already exists.")
        return super().clean()
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        add_error = partial(self.add_error, "phone_number")
        if not phone_number:
            add_error("Phone Number must not be empty.")
        if not bool(NIGERIA_PHONE_NUMBER.match(phone_number)):
            add_error("Phone Number not match.")
        if Client.objects.filter(phone_number__iexact=phone_number).exists():
            add_error("Something Went Wrong.")
        return phone_number


    def save(self, commit = True):
        instance = super().save(commit=False)
        if getattr(settings, "USE_ACCOUNT_ACTIVATION_VIEW", True):
            instance.is_active = False # Prevent user to login
        if commit:
            instance.save()
        phone_number = self.cleaned_data["phone_number"]
        try:
            instance.client.phone_number = phone_number
            instance.client.save()
        except AttributeError:
            pass
        return instance
    
    def send_email(self, request, user, subject="", body=None):
        
        assert (
            (request.user.is_authenticated or user.is_active) or \
            not getattr(settings, "USE_ACCOUNT_ACTIVATION_VIEW", True)
        )
        
        if not subject:
            subject = _("Account Activation")
        token_generator = default_token_generator
        token = token_generator.make_token(user)
        if body is None:
            body = self.email_body(request, user_id=user.pk, token=token)
        mail.EmailMessage(
            subject,
            body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.cleaned_data["email"]]
        ).send(not settings.DEBUG)

    
    def email_body(self, request, user_id, token=""):
        return (
            get_template("email-body.txt").\
                render(context=self.get_email_body_context(request, user_id, token))
        )

    def get_email_body_context(self, request, user_id, token):
        kwargs = {}
        
        url = reverse("account_activation", kwargs={"token": token, "user_id": user_id})
        url = request.build_absolute_uri(url)
        kwargs["url"] = url
        kwargs["name"] = self.cleaned_data["username"]
        return kwargs

