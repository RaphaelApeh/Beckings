from typing import Any, final

from django import template
from django.template.base import (
    Token, Parser
)
from django.forms import BoundField


register = template.Library()

DEFAULT_TAILWIND_CSS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"


def do_render_field(parser: Parser, token: Token):
    """ Usage {% render_field "form.name" class="btn-class" %} """
    _, *bits = token.split_contents()
    if len(bits) < 1:
        msg = ""
        raise template.TemplateSyntaxError(msg)
    form_field = parser.compile_filter(bits.pop(0))
    class_attr = []
    if bits:
        for bit in bits:
            k, v = bit.split("=")
            v = parser.compile_filter(v)
            class_attr.append((k, v))
    
    return FieldRenderNode(form_field, class_attr)

@final
class FieldRenderNode(template.Node):

    def __init__(self, form_field, class_attr: list[tuple[Any]]):
        
        self.form_field = form_field
        self.class_attr = class_attr

    def render(self, context):
        
        boundfield = self.form_field.resolve(context) #noqa
        field = boundfield.field
        kwargs = self._parse_class_attr(context)
        field.widget.attrs.update(kwargs)
        return str(boundfield)
    
    def _parse_class_attr(self, context) -> dict[Any]:
        kwargs = {}
        if class_attr := self.class_attr:
            for k, v in class_attr:
                kwargs[k] = v.resolve(context)
        return kwargs


def do_form_class(field: BoundField, class_attr: str | None = None) -> BoundField:

    if not isinstance(field, BoundField):
        return field
    class_attr = class_attr if class_attr is not None else DEFAULT_TAILWIND_CSS

    field.field.widget.attrs.setdefault("class", class_attr)

    return field


register.filter("form_class", do_form_class)
register.tag("render_field", do_render_field)
