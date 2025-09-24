from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View
from django.core.exceptions import ImproperlyConfigured


class FormsetMixin(TemplateResponseMixin, ContextMixin):

    form_class = None
    formset_class = None

    def formset_valid(self, request, formset):
        raise NotImplementedError

    def formset_invalid(self, request, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_formset_class(self):

        if (formset_class := self.formset_class) is not None:
            return formset_class

        formset_class = formset_factory(**self.get_formset_class_kwargs())
        return formset_class

    def get_formset_class_kwargs(self):
        form_class = self.form_class
        if form_class is None:
            raise ImproperlyConfigured(
                f"attribute 'form_class' must be set in {self.__class__.__name__}"
            )
        return {"form": form_class}

    def get_formset(self, request, formset_class=None):
        formset_class = formset_class or self.get_formset_class()
        formset = formset_class(**self.get_formset_kwargs(request))
        return formset

    def post(self, request, *args, **kwargs):

        formset = self.get_formset(request)
        if formset.is_valid():
            return self.formset_valid(request, formset)
        return self.formset_invalid(request, formset)

    def get_formset_initial(self, request):
        return {}

    def get_formset_kwargs(self, request):
        return {
            "data": request.POST or None,
            "files": request.FILES or None,
            "initial": self.get_formset_initial(request),
        }

    def get_context_data(self, **kwargs):
        formset = self.get_formset(self.request)

        kwargs.setdefault("formset", formset)
        kwargs.setdefault("management", formset.management_form)
        kwargs.setdefault("empty_form", formset.empty_form)
        return super().get_context_data(**kwargs)


class ModelFormsetMixin(FormsetMixin):

    fields = None
    exclude = None
    model = None
    queryset = None
    success_url = None
    for_creation = False
    template_suffix = "_formset"

    def get_queryset(self):
        if (model := self.model) is not None:
            return model._default_manager.all()
        if (qs := self.queryset) is not None:
            return qs.all()
        raise ImproperlyConfigured(
            "%(cls)s is missing a QuerySet. Define "
            "%(cls)s.model, %(cls)s.queryset, or override "
            "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
        )

    def get_formset_class(self):

        if self.formset_class and self.form_class:
            raise ImproperlyConfigured(
                "Cannot set both %(cls)s.formset_class and %(cls)s.form_class"
                % ({"cls": self.__class__.__name__})
            )
        if self.formset_class:
            return self.formset_class

        return modelformset_factory(**self.get_formset_class_kwargs())

    def get_formset_class_kwargs(self):

        if self.form_class and self.fields:
            raise ImproperlyConfigured(
                "can't have both 'form_class' and 'fields' set.\n"
                "hint: Set 'form_class' or 'fields' to None."
            )
        kwargs = {}
        model = self.get_queryset().model

        extra = None
        if self.for_creation:
            extra = 1
        kwargs.update({"model": model, "extra": extra})
        if self.form_class:
            kwargs["form"] = self.form_class
        elif self.fields:
            kwargs["fields"] = self.fields
            kwargs["exclude"] = self.exclude
        return kwargs

    def get_formset_kwargs(self, request):

        kwargs = super().get_formset_kwargs(request)
        qs = self.get_queryset()
        if self.for_creation:
            qs = qs.none()
        kwargs.update({"queryset": qs})
        return kwargs

    def get_template_names(self):

        if isinstance(self.template_name, str):
            template_name = (self.template_name,)
        else:
            template_name = self.template_name
        if template_name:
            return template_name

        opts = self.get_queryset().model._meta
        template_name = ("%(app_label)s/%(model_name)s%(suffix)s.html") % {
            "app_label": opts.app_label,
            "model_name": opts.object_name.lower(),
            "suffix": self.template_suffix,
        }
        return (template_name,)

    def formset_valid(self, request, formset):
        formset.save()
        return HttpResponseRedirect(redirect_to=self.get_success_url())

    def get_success_url(self):
        if (url := self.success_url) is not None:
            return url
        raise ImproperlyConfigured(
            "%s.success_url must be defined." % self.__class__.__name__
        )


class ModelFormsetView(ModelFormsetMixin, View):
    """
    Model formset View

    Attributes:
        template_name (str)
        model (Model, optional)
        queryset (Queryset, optional)
        formset_class (BaseFormset, optional)
        success_url (str, optional)
        for_creation (bool)
        form_class (Form, optional)
        fields (list, optional)
        exclude (list, optional)

    Example:
        >>> class AuthorCreateView(ModelFormsetView):
        ...          model = Author
        ...          template_name = "authors/create.html"
        ...          formset_class = AuthorFormset
        ...          for_creation = True
    """

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)
