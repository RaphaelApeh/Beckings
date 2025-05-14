from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    DetailView
    )
from django.shortcuts import get_object_or_404, render

from helpers.decorators import require_htmx

from .models import Product


class ProductListView(View):

    queryset = Product.objects.select_related("user").all()
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


    def get_object(self, queryset = None) -> Product:

        model = queryset.model if queryset is not None else None or self.get_queryset().model
        kwargs = {"pk": self.kwargs["pk"], "product_slug": self.kwargs["slug"]}
        obj = get_object_or_404(model, **kwargs)

        return obj


@method_decorator(require_htmx, name="dispatch")
class ProductSearchView(View):

    def get(self, request: HttpRequest) -> HttpResponse:

        context = {}
        query = request.GET.get("q")
        queryset = Product.objects.all()
        if query:
            queryset.filter(product_name=query).order_by("-timestamp")
        else:
            queryset.none()
        
        context["queryset"] = queryset

        return render(request, "products/partials/product_list.html", context)
    

product_search_view = ProductSearchView.as_view()

