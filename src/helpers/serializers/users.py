from typing import Any, TypeVar, Optional, Union, NoReturn

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.views.decorators.debug import sensitive_variables
from django.utils.decorators import method_decorator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import qs_exists
from rest_framework.exceptions import APIException

from clients.models import Client
from helpers._typing import AuthUser
from helpers.validators import PhoneNumberValidator
from .token import PasswordField


UserType = TypeVar("UserType", AbstractUser, AuthUser)

User = get_user_model()


class _APIException(APIException):

    status_code = 404
    default_detail = "error"


def validate_user_field(
    instance: UserType, field: Union[str, None] = None, value: Optional[str] = None
) -> NoReturn:

    qs = User.objects.filter(is_active=True).exclude(pk=instance.pk)
    if field and value:
        qs = qs.filter(**{f"{field}__iexact": value})
    if qs_exists(qs):
        raise serializers.ValidationError(
            "%(value)s already exists." % {"value": value}
        )


class PhoneNumberField(serializers.CharField):
    """
    Serializer Field for Internal Phone Number
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        validator = PhoneNumberValidator()
        self.validators.append(validator)


class UsernameField(serializers.CharField):

    default_error_messages = {"invalid": _("Enter a valid Username.")}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        validator = UnicodeUsernameValidator(
            message=self.default_error_messages["invalid"]
        )
        self.validators.append(validator)


@method_decorator(
    sensitive_variables("old_password", "new_password", "confirmation_password"),
    name="validate",
)
class ChangePasswordSerializer(serializers.Serializer):

    old_password = PasswordField()

    new_password = PasswordField()

    confirmation_password = PasswordField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)

        old_password = data.pop("old_password", None)

        new_password = data.pop("new_password", None)
        confirmation_password = data.pop("confirmation_password")

        if new_password != confirmation_password:
            raise _APIException("Password not match.")
        try:
            validate_password(new_password)

        except ValidationError as e:
            raise _APIException(" ".join(e.messages))

        user: UserType = self.context["request"].user

        if not user.check_password(old_password):
            raise _APIException("incorrect password.")

        user.set_password(new_password)
        user.save()
        return {}


@method_decorator(
    sensitive_variables("password1", "password2", "email"), name="validate"
)
class UserCreationSerializer(serializers.Serializer):

    username = UsernameField()
    email = serializers.EmailField()
    phone_number = PhoneNumberField()
    password1 = PasswordField()
    password2 = PasswordField()

    def validate_phone_number(self, value) -> str:
        match value:
            case v if v is None:
                raise serializers.ValidationError("phone_number field can't be null")
            case _:
                if not Client.objects.filter(phone_number__iexact=value).exists():
                    raise serializers.ValidationError("Something went wrong :(")
        # re-validate the value
        validator = PhoneNumberValidator()
        validator(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:

        username = attrs.pop("username")
        email = attrs.pop("email")
        phone_number = attrs.pop("phone_number")
        password1 = attrs.pop("password1")
        password2 = attrs.pop("password2")

        try:
            validate_password(password1)
        except ValidationError as err:
            raise serializers.ValidationError(" ".join(err.messages))

        if password1 != password2:
            raise serializers.ValidationError(_("Password not Match."))

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                _("A User with this email already exists.")
            )

        obj = User.objects.create_user(username, email, password1)

        data = {
            "message": _("User created Successfully."),
            "user": {"id": obj.pk, "username": obj.username, "email": obj.email},
        }
        try:
            obj.client.phone_number = phone_number
            obj.client.save()
        except AttributeError:
            pass
        else:
            data["user"]["phone_number"] = phone_number

        return data


class UserUpdateSerializer(serializers.Serializer):

    UNIQUE_FIELDS = ["username", "email"]

    username = UsernameField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:

        if self.instance is None or self.initial_data is None:
            raise serializers.ValidationError("an error ocured.")

        if not attrs:
            raise serializers.ValidationError("data is null.")

        data = {"message": _("details updated.")}
        instance = self.instance

        with transaction.atomic():

            for key, value in attrs.items():

                if not hasattr(instance, key):
                    continue
                if key in self.UNIQUE_FIELDS:
                    validate_user_field(instance, field=key, value=value)
                setattr(instance, key, value)

            instance.save()

        return data
