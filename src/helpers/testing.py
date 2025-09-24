from contextlib import contextmanager
from typing import TypeVar, Generator, Any

from django.utils.module_loading import import_string
try:
    import factory as fty
    factory_boy = True
except ImportError:
    factory_boy = False

FactoryType = TypeVar("FactoryType")


@contextmanager
def create_factory(
    factory: FactoryType | str, 
    *, 
    size=1) -> Generator[None, Any, None]:

    assert not (not factory_boy)
    if isinstance(factory, str):
        factory = import_string(factory)
    elif not isinstance(factory, fty.base.BaseFactory):
        raise TypeError(
            "Got an unexcepted type:\n %s" % factory
        )

    assert factory is not None
    
    factory.create_batch(size)
    yield
