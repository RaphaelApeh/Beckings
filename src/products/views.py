from django.views.generic import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Product


class ProductListView(View):

    queryset = Product.objects.all()
    template_name = "products/product_list.html"
    

    def get(self, request: HttpRequest) -> HttpResponse:

        queryset = self.queryset
        
        if hasattr(request, "htmx") and request.htmx:
            queryset = queryset.filter()

        context = {"queryset": queryset}
        template_name = self.template_name

        return render(request, template_name, context)
    

