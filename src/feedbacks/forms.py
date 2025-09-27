from django import forms
from django.contrib.auth import get_user_model

from helpers.forms.mixins import TailwindRenderFormMixin
from .models import FeedBack, ComplainType


UserModel = get_user_model()


class FeedBackMixin:

    def save(self, commit=True):
        model = self.model
        if "user" in self.cleaned_data:
            user = self.cleaned_data.pop("user", None)
            _, _instance = model.objects.create_for_user(user, **self.cleaned_data)
            return _instance
        instance = None
        if hasattr(super(), "save"):
            instance = super().save(commit)
        if instance is None:
            instance = model.objects.create(**self.cleaned_data)
        return instance


class FeedBackForm(TailwindRenderFormMixin, FeedBackMixin, forms.Form):

    non_user_fields = ("user",)

    email = forms.EmailField(
        label="Your Email"
    )
    user = forms.ModelChoiceField(
        UserModel._default_manager.filter(is_active=True),
        widget=forms.HiddenInput,
        required=False
    )
    complain = forms.CharField(
        widget=forms.Textarea
    )
    complain_type = forms.ChoiceField(
        choices=ComplainType.choices
    )

    def __init__(self, user=None, *args, **kwargs):
        self.model = FeedBack
        super().__init__(*args, **kwargs)
        non_user_fields = self.non_user_fields
        if not user and non_user_fields:
            for name in non_user_fields:
                del self.fields[name]
        elif user:
            del self.fields["email"]
