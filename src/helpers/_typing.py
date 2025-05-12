from typing import Any

from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails


__all__ = [
    "HTMXHttpRequest",
    "Bit"
]

class HTMXHttpRequest(HttpRequest):

    htmx: HtmxDetails


Bit = dict[str, Any]