from __future__ import annotations

from typing import Any, Optional

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    ListView,
    DetailView,
    FormView,
    CreateView
    )
from django.views.generic.edit import ModelFormMixin
from django.shortcuts import get_object_or_404, render
from django.contrib.admin.views.decorators import staff_member_required

from django_htmx.http import HttpResponseClientRedirect

from helpers.decorators import require_htmx

from clients.views import \
        FormRequestMixin
from .models import Product, \
                    OrderProxy
from .forms import AddOrderForm, \
                    ProductForm


class ProductListView(ListView):

    queryset = Product.objects.select_related("user").filter(active=True)
    template_name = "products/product_list.html"
    context_object_name = "queryset"


class ProductDetailView(FormRequestMixin, 
                        ModelFormMixin, 
                        DetailView):
    http_method_names = (
        "get",
        "post",
        "put",
        "delete"
    )
    model = Product
    template_name = "products/product-detail.html"
    query_pk_and_slug = True
    form_class = ProductForm

    def get_template_names(self):
        if self.request.htmx:
            return ["products/partials/product_update.html"]
        return super().get_template_names()

    def get(self, request, *args, **kwargs):
        if self.request.htmx:
            return self.htmx_get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    
    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def htmx_get(self, request, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.get_object()})
        return kwargs

    def get_object(self, queryset = None) -> Product:

        model = queryset.model if queryset is not None else None or self.get_queryset().model
        kwargs = {"pk": self.kwargs["pk"], "product_slug": self.kwargs["slug"]}
        obj = get_object_or_404(model, **kwargs)
        self.object = obj
        return obj

    def delete_object(self, instance):
        instance.delete()

    def form_valid(self, form):
        form.save()
        self.object.refresh_from_db()
        return HttpResponseClientRedirect(self.object.get_absolute_url())

    def delete(self, request, *args, **kwargs):
        self.delete_object(self.get_object())
        return HttpResponseClientRedirect(reverse("products"))


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
        kw.setdefault("view", self)
        return kw

    def form_valid(self, form) -> HttpResponse:
        kwargs = {
            "user": self.request.user
        } # empty for now
        form.save(**kwargs)
        return HttpResponseClientRedirect(self.product.get_absolute_url())


@method_decorator(staff_member_required(login_url="login"), name="dispatch")
class ProductCreateView(FormRequestMixin, CreateView):

    template_name = "products/product_create.html"
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        kwargs["title"] = "Create Product"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


product_create_view = ProductCreateView.as_view()