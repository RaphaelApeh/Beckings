from typing import Any

from django import forms
from django.forms.utils import pretty_name



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

        for field in self.fields:
            self.fields[field].widget.attrs.setdefault("placeholder", pretty_name(field))
        


    manifest = TextField(required=False, help_text="Your Address")
    number_of_items = forms.IntegerField()


    def clean(self):
        data = self.cleaned_data

        return data

    
    def save(self, **kwargs: Any) -> None:
        
       ... 

