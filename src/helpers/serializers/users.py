from typing import Any, TypeVar

from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.views.decorators.debug import sensitive_variables
from django.utils.decorators import method_decorator
from django.contrib.auth.validators import \
                            UnicodeUsernameValidator
from django.contrib.auth.password_validation import \
        validate_password

from rest_framework import serializers
from rest_framework.exceptions import APIException

from helpers._typing import AuthUser
from .token import PasswordField


UserType = TypeVar("UserType", AbstractUser, AuthUser)

User = get_user_model()

class _APIException(APIException):

    status_code = 404
    default_detail = "error"


class UsernameField(serializers.CharField):


    default_error_messages = {
        'invalid': _('Enter a valid Username.')
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        validator = UnicodeUsernameValidator(message=self.default_error_messages["invalid"])
        self.validators.append(validator)


@method_decorator(sensitive_variables("old_password",
                                       "new_password", 
                                       "confirmation_password"),
                                       name="validate")
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


@method_decorator(sensitive_variables("password1", "password2", "email"), name="validate")
class UserCreationSerializer(serializers.Serializer):

    username = UsernameField()
    email = serializers.EmailField()
    password1 = PasswordField()
    password2 = PasswordField()

    
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        
        username = attrs.pop("username")
        email = attrs.pop("email")
        password1 = attrs.pop("password1")
        password2 = attrs.pop("password2")

        try:
            validate_password(password1)
        except ValidationError as err:
            raise serializers.ValidationError(" ".join(err.messages))
        
        if password1 != password2:
            raise serializers.ValidationError(_("Password not Match."))
        
        obj = User.objects.create_user(username,
                                 email,
                                 password1)
        
        data = {
            "message": _("User created Successfully."),
            "user": {
            "id": obj.pk,
            "username": obj.username,
            "email": obj.email
            }
        }

        return data