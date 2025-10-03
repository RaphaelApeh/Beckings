from typing import Dict

from django.views import generic
from django.contrib import messages
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from .models import FeedBack
from .forms import FeedBackForm


def get_user_or_None(request, raise_exception=False):
    assert request is not None
    user_ = (
        user if (user := request.user) and request.user.is_authenticated else None
    )
    if user_ is None and raise_exception:
        raise TypeError(
            "Expected a auth.User model instance but got\n",
            "(%s)" % type(user_).__name__
        )
    return user_


class FeedBackCreateView(generic.FormView):

    form_class = FeedBackForm
    model = FeedBack
    template_name = "feedbacks/create_feedback.html"
    success_template_name = "feedbacks/success.html"
    title = _("Send You Feed back.")


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = get_user_or_None(self.request)
        initial = kwargs.get("initial") or {}
        initial.setdefault("user", user)
        kwargs["initial"] = initial
        return kwargs
    
    def get_context_data(self, **kwargs) -> Dict:
        user = get_user_or_None(self.request)
        if user is None:
            input_html = ""
        else:
            input_html = format_html('<input type="hidden" name="user" value="{}" />', str(user.pk))
        msg = _("Feed back sent.")
        kwargs.setdefault("msg", msg)
        kwargs.setdefault("title", self.title)
        kwargs["user_html_field"] = input_html
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        request = self.request
        user, obj = form.save()
        self.object = obj
        messages.success(request, _("Feed back successfully sent."))
        # request.user might be AnonymousUser
        return TemplateResponse(
            request,
            self.success_template_name,
            self.get_context_data(object=obj, user_obj=user)
        )