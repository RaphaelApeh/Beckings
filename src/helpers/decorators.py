from typing import Any
from typing import Callable, TypeVar
from functools import wraps

from django.http import HttpResponse
from django.http import HttpResponseBadRequest

from rest_framework.pagination import BasePagination

from helpers._typing import HTMXHttpRequest


T = TypeVar("T")

try:
    from django.utils.functional import classproperty
except ImportError:
    class classproperty:

        def __init__(self, fget: Callable[..., Any]) -> None:

            self.fget = fget
        
        def __get__(self, instance: T, cls=None) -> Callable[..., Any]:

            assert cls is not None

            return self.fget(cls)
        
        def getter(self, func):
            self.fget = func


def paginate[T](pagination_class: T, **kwargs: dict[str, Any]) -> Any:
    
    """
    Decorator for paginating a function base view. \n
    Example:
    >>> @paginate(PageNumberPagination, page_size=3)
    >>> class UserAPIView(View):
    >>>     queryset = User.objects.all()
    >>>     
    """

    assert issubclass(pagination_class, BasePagination)

    Paginator = type("Paginator", (pagination_class,), kwargs)


    def _inner[C](cls) -> C:

        cls.pagination_class = Paginator

        return cls
    
    return _inner



def require_htmx(view_func: Callable[[], HttpResponse]) -> Callable[[], Any]:
     
    @wraps(view_func)
    def inner(request: HTMXHttpRequest, *args, **kwargs) -> HttpResponse:

        if hasattr(request, "htmx") and request.htmx:
            return view_func(request, *args, **kwargs)
        
        return HttpResponseBadRequest()

    return inner


