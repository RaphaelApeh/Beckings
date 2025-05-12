from typing import Any
from typing import Callable
from functools import wraps

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from helpers._typing import HTMXHttpRequest


def require_htmx(view_func: Callable[[], HttpResponse]) -> Callable[[], Any]:
     
    @wraps(view_func)
    def inner(request: HTMXHttpRequest, *args, **kwargs) -> HttpResponse:

        if hasattr(request, "htmx") and request.htmx:
            return view_func(request, *args, **kwargs)
        
        raise PermissionDenied()

    return inner


