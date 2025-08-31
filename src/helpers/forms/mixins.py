from django.forms.utils import RenderableMixin
from django.utils.safestring import SafeText


class TailwindRenderFormMixin(RenderableMixin):

    template_name_tailwind = "helpers/forms/tailwind.html"
    template_name_tailwind_table = "helpers/forms/table.html"

    def as_tailwind(self) -> SafeText:

        assert hasattr(self, "get_context")
        return self.render(self.template_name_tailwind)

    def as_tailwind_table(self) -> SafeText:

        return self.render(self.template_name_tailwind_table)
