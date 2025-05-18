from typing import Any
from typing import Callable
from functools import wraps

from django.http import HttpResponse
from django.http import HttpRequest
from django.db.models import QuerySet
from django.http import HttpResponseBadRequest

from rest_framework.response import Response
from rest_framework.pagination import BasePagination

from helpers._typing import HTMXHttpRequest



def paginate[T](pagination_class: T, **kwargs: dict[str, Any]) -> Callable[[], Any]:
    
    """
    Decorator for paginating a function base view. \n
    Example:
    >>> @api_view(["GET"])
    >>> @paginate(PageNumberPagination, page_size=3)
    >>> def list_users_view(request):
    >>>     users = User.objects.all()
    >>>     return users, UserSerializer(users).data
    """

    assert issubclass(pagination_class, BasePagination)

    Paginator = type("Paginator", (pagination_class,), kwargs)

    def inner(func: Callable[[], dict[str, Any]]) -> Callable[[], Response]:

        @wraps(func)
        def _warpper(request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
            
            data = func(request, *args, **kwargs)

            queryset = data["queryset"]
            assert isinstance(queryset, QuerySet)

            paginator = Paginator()
            paginator.paginate_queryset(queryset, request)

            return paginator.get_paginated_response(data["data"])


        return _warpper

    return inner



def require_htmx(view_func: Callable[[], HttpResponse]) -> Callable[[], Any]:
     
    @wraps(view_func)
    def inner(request: HTMXHttpRequest, *args, **kwargs) -> HttpResponse:

        if hasattr(request, "htmx") and request.htmx:
            return view_func(request, *args, **kwargs)
        
        return HttpResponseBadRequest()

    return inner


