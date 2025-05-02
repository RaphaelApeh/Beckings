from django.http import HttpRequest, HttpResponse
from django.views.generic import (
    View,
    DetailView
    )
from django.shortcuts import get_object_or_404, render

from .models import Product


class ProductListView(View):

    queryset = Product.objects.all()
    template_name = "products/product_list.html"
    

    def get(self, request: HttpRequest) -> HttpResponse:

        queryset = self.queryset

        context = {"queryset": queryset}

        if hasattr(request, "htmx") and request.htmx:
            queryset = queryset.filter()

        template_name = self.template_name
        return render(request, template_name, context)
    


class ProductDetailView(DetailView):

    model = Product
    template_name = "products/product-detail.html"
    query_pk_and_slug = True

    def get_object(self, queryset = None):

        #assert isinstance(queryset, QuerySet)
        model = queryset.model if queryset is not None else None or self.get_queryset().model
        kwargs = {"pk": self.kwargs["pk"], "product_slug": self.kwargs["slug"]}
        obj = get_object_or_404(model, **kwargs)

        return obj

