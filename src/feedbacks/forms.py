from django import forms
from django.contrib.auth import get_user_model

from helpers.forms.mixins import TailwindRenderFormMixin
from .models import ComplainType


UserModel = get_user_model()

class FeedBackForm(TailwindRenderFormMixin, forms.Form):

    non_user_fields = ("user",)

    email = forms.EmailField()
    user = forms.ModelChoiceField(
        UserModel._default_manager.filter(is_active=True),
        widget=forms.HiddenInput,
        label="Your Email",
        required=False
    )
    complian = forms.CharField(
        widget=forms.Textarea
    )
    complian_type = forms.ChoiceField(
        choices=ComplainType.choices
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        non_user_fields = self.non_user_fields
        if not user and non_user_fields:
            for name in non_user_fields:
                del self.fields[name]
        elif user:
            del self.fields["email"]
