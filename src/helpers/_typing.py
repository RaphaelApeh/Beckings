from typing import Any

from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails


__all__ = [
    "HTMXHttpRequest",
    "Bit",
    "AuthUser",
]

class HTMXHttpRequest(HttpRequest):

    htmx: HtmxDetails


Bit = dict[str, Any]

List = list[str]


class AuthUser:

    username: str
    email : str | None
    first_name : str | None
    last_name : str | None
    groups : set | None


    @property
    def user_permissions(self) -> set:
        return set()


    @property
    def is_authenticated(self) -> bool:
        return True


    @property
    def is_anonymous(self) -> bool:
        return False
    


