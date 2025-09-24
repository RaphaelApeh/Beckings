from typing import Any

from django.conf import settings
from django.http import HttpRequest


def default_price(request: HttpRequest) -> dict[str, Any]:

    return {"DEFAULT_PRICE_CURRENCY": getattr(settings, "DEFAULT_PRICE_CURRENCY", "$")}
