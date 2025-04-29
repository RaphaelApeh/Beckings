from typing import Any
from typing import Callable
from functools import wraps

from django.http import HttpRequest
from django.db.models import QuerySet

from rest_framework.response import Response
from rest_framework.pagination import BasePagination


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

    class Paginator(pagination_class):

        def __init__(self) -> None:

            for key, value in kwargs.items():
                assert hasattr(self, key), f"{pagination_class.__name__} has no attribute {key}"
                if callable(value):
                    raise TypeError
                setattr(self, key, value)

            self.__doc__ = pagination_class.__doc__

    def inner(func: Callable[[], tuple[QuerySet, dict]]) -> Callable[[], Response]:

        @wraps(func)
        def _warpper(request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
            
            queryset, data = func(request, *args, **kwargs)

            assert isinstance(queryset, QuerySet)

            paginator = Paginator()
            paginator.paginate_queryset(queryset, request, func)

            return paginator.get_paginated_response(data)


        return _warpper

    return inner

