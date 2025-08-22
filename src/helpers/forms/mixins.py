from django.forms.utils import RenderableMixin


class TailwindRenderFormMixin(RenderableMixin):

    template_name_tailwind = "helpers/forms/tailwind.html"

    def as_tailwind(self) -> str:

        assert hasattr(self, "get_context")
        return self.render(self.template_name_tailwind)
