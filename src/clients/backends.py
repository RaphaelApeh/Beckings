from typing import Unpack
from typing import TypedDict

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class _EmailAuth(TypedDict):

    username : str
    password : str


class EmailBackend(ModelBackend):

    def authenticate(self, request, **kwargs: Unpack[_EmailAuth]):

        email = kwargs["username"]
        password = kwargs["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
            return None

        
