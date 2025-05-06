from django.template import Library
from django.forms import BoundField


register = Library()

DEFAULT_TAILWIND_CSS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"


def do_form_class(field: BoundField, class_attr: str | None = None) -> BoundField:

    class_attr = class_attr if class_attr is not None else DEFAULT_TAILWIND_CSS

    field.field.widget.attrs.setdefault("class", class_attr)

    return field


register.filter("form_class", do_form_class)

