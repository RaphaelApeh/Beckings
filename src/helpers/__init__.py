from django.http import HttpRequest


def parse_request[T](args: list[T], raise_exception=False) -> HttpRequest | None:
    _request = None

    for bit in args:
        if isinstance(bit, HttpRequest):
            _request = HttpRequest
            break
    if raise_exception and _request is None:
        raise TypeError
    return _request

