from typing import Callable

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from helpers._typing import HTMXHttpRequest


def htmx_required(view_func: Callable[[], HttpResponse]):
     

    def inner(request: HTMXHttpRequest, *args, **kwargs):

        if request.htmx:
            return view_func(request, *args, **kwargs)
        
        raise PermissionDenied()

    return inner


