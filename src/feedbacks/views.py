from typing import Dict

from django.views import generic
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from .models import FeedBack
from .forms import FeedBackForm

class FeedBackCreateView(generic.CreateView):

    form_class = FeedBackForm
    model = FeedBack
    template_name = "feedbacks/create_feedback.html"
    success_template_name = "feedbacks/success.html"
    title = _("Send You Feed back.")

    def get_form_kwargs(self) -> Dict:
        user = (
            user if (user := self.request.user) and not user.is_anonymous else None
        )
        return {**super().get_form_kwargs(), "user": user}
    
    def get_context_data(self, **kwargs):
        kwargs.setdefault("title", self.title)
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