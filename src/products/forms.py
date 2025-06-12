from __future__ import annotations

from typing import Any

from django import forms
from django.forms.utils import pretty_name

from .order_utils import AddOrder

class TextField(forms.CharField):
    
    widget = forms.Textarea


class AddOrderForm(forms.Form):


    def __init__(self, *args: Any, **kwargs: Any) -> None:

        request = kwargs.pop("request", None)
        view = kwargs.pop("view", None)

        assert request is not None and \
                view is not None

        super().__init__(*args, **kwargs)
        
        self.request = request
        self.view = view

        for field in self.fields:
            self.fields[field].widget.attrs.setdefault("placeholder", pretty_name(field))
        self.fields["number_of_items"].widget.attrs.update({"min": 0})        


    manifest = TextField(required=False)
    number_of_items = forms.IntegerField()


    def clean(self):

        data = self.cleaned_data
        
        product_instance = self.product
        number_of_items = data.get("number_of_items", 0)

        match number_of_items:
            case 0:
                self.add_error(None, "Can not add an empty order.")
            case n if n < 1:
                self.add_error(None, "Can't add nagative item")
            case s if s > product_instance.quantity:
                self.add_error(None, "Not enough quantity to order.")
            case _:
                pass
        return data
    
    @property
    def product(self):
        if not hasattr(self, "_product"):
            self._product = getattr(self.view, "product")
        return self._product
    

    def save(self, user, **kwargs: Any) -> None:
       data = self.cleaned_data
       
       AddOrder(
           product_instance=self.product
       ).create(user, data)

