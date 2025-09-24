from typing import Unpack
from typing import TypedDict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class _EmailAuth(TypedDict):

    username: str
    password: str


class EmailBackend(ModelBackend):

    def authenticate(
        self, request, **kwargs: Unpack[_EmailAuth]
    ) -> AbstractBaseUser | None:

        email = kwargs["username"]
        password = kwargs["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:

            User().set_password(password)
            return None
        else:
            if user.check_password(password) and user.is_active:
                return user
            return None
