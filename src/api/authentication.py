from typing import Union, TypeVar, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import TokenAuthentication as BaseTokenAuthentication
from rest_framework import exceptions

from .models import Token, get_token_model


T = TypeVar("T")


class TokenAuthentication(BaseTokenAuthentication):
    """
    Overiding the base token authentication
    """

    model: Union[Token, None] = get_token_model()

    def authenticate_credentials(self, key: str) -> tuple[T, Optional[str]]:
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        if hasattr(token, "is_expired") and token.is_expired():
            raise exceptions.AuthenticationFailed(_("Token expired."))

        return (token.user, token)
