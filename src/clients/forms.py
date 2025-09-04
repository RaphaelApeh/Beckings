from functools import partial

from django import forms
from django.core import mail
from django.conf import settings
from django.urls import reverse
from django.forms.models import construct_instance
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
from helpers.forms.mixins import TailwindRenderFormMixin
from helpers.validators import validate_phone_number

User = get_user_model()


class PasswordField(forms.CharField):

    widget = forms.PasswordInput


class EmailCheckMixin:

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email__iexact=email).exists():
            return email
        self.add_error("email", "Email already exists.")


class PhoneNumberCheckMixin(EmailCheckMixin):

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        add_error = partial(self.add_error, "phone_number")
        if not phone_number:
            add_error("Phone Number must not be empty.")
        if not bool(NIGERIA_PHONE_NUMBER.match(phone_number)):
            add_error("Phone Number not match.")
        validate_phone_number(phone_number)
        return phone_number


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


class RegisterForm(PhoneNumberCheckMixin, UserCreationForm):

    phone_number = forms.RegexField(
        regex=PHONE_NUMBER_REGEX,
        widget=forms.TelInput({
            "pattern": PHONE_NUMBER_REGEX,
            "title": "Enter a valid phone number e.g(+2348139582053)"
        })
    )

    field_order = ("username", "email", "phone_number")
        
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = ""
            self.fields[field].widget.attrs.update({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"})


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
        
        if request.user.is_authenticated or user.is_active or not \
            getattr(settings, "USE_ACCOUNT_ACTIVATION_VIEW", True):
            return
        
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


class AccountForm(PhoneNumberCheckMixin, TailwindRenderFormMixin, forms.ModelForm):

    field_order = (
        "username",
        "first_name",
        "last_name",
        "email",
        "address",
        "phone_number"
    )

    address = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    phone_number = forms.RegexField(
    regex=PHONE_NUMBER_REGEX,
    widget=forms.TelInput({
        "pattern": PHONE_NUMBER_REGEX,
        "title": "Enter a valid phone number e.g(+2348139582053)"
    })
    )
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",

        )
        
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._init_client()

    
    def _init_client(self) -> None:

        user = self.instance
        try:
            instance = Client.objects.get(user_id=user.pk)
        except Client.DoesNotExist:
            print("Error")
            return
        instance_dict = forms.model_to_dict(instance, exclude=["user"])
        self.initial.update(instance_dict)

    
    def save(self, commit=True):
        instance = super().save(commit)
        obj = instance.client
        obj = (
            construct_instance(
                self, obj, 
                fields=["phone_number", "address"]
            )
        )
        obj.save()        
        return instance
