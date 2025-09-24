from django.template.loader import render_to_string
from django.forms.utils import RenderableMixin
from django.utils.safestring import SafeText


class TailwindRenderFormMixin(RenderableMixin):
    """Helper mixin for adding tailwind css to Forms"""

    template_name_tailwind = "helpers/forms/tailwind.html"
    template_name_tailwind_table = "helpers/forms/table.html"

    def as_tailwind(self) -> SafeText:
        """Render form fields with tailwind css classes"""
        return render_to_string(self.template_name_tailwind, self.get_context())

    def as_tailwind_table(self) -> SafeText:

        return render_to_string(self.template_name_tailwind_table, self.get_context())

    @property
    def labels(self) -> list[str]:
        labels = []
        for field in self.visible_fields:
            labels.append(field.label)
        return labels
