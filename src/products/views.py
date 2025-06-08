from __future__ import annotations

from typing import Any, Optional

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    ListView,
    DetailView,
    FormView
    )
from django.shortcuts import get_object_or_404, render

from django_htmx.http import HttpResponseClientRedirect

from helpers.decorators import require_htmx

from clients.views import \
        FormRequestMixin
from .models import Product, \
                    OrderProxy
from .forms import AddOrderForm


class ProductListView(ListView):

    queryset = Product.objects.select_related("user")
    template_name = "products/product_list.html"
    context_object_name = "queryset"


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
            queryset = queryset.filter(product_name__icontains=query).order_by("-timestamp")
        
        context["queryset"] = queryset

        return render(request, "products/partials/product_list.html", context)
    

product_search_view = ProductSearchView.as_view()


@method_decorator(login_required, name="dispatch")
class UserOrderListView(ListView):

    queryset = OrderProxy.objects.select_related("user", "product")   
    template_name = "orders/order_list.html"



@method_decorator([login_required, require_htmx], name="dispatch")
class AddOrderView(FormRequestMixin, FormView):

    template_name: Optional[str] = "orders/add_order.html"
    form_class = AddOrderForm


    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        
        kw = {
            "pk": kwargs.get("product_id")
        }
        product = get_object_or_404(Product, **kw)
        self.product = product
        return super().dispatch(request, *args, **kwargs)


    def get_form_kwargs(self) -> dict[str, Any]:
        kw = super().get_form_kwargs()
        kw["view"] = self
        return kw

    def form_valid(self, form) -> HttpResponse:
        kwargs = {} # empty for now
        form.save(**kwargs)
        return HttpResponseClientRedirect(self.product.get_absolute_url())


