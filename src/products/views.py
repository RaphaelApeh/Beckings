from __future__ import annotations

from typing import Any, Optional, TypeVar, NoReturn

from django.urls import reverse
from django.db.models import QuerySet
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    ListView,
    DetailView,
    FormView,
    CreateView
    )
from django.http import (HttpRequest, 
                         HttpResponse, 
                         HttpResponseRedirect,
                        )
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import ModelFormMixin
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required

from django_htmx.http import HttpResponseClientRedirect

from helpers.decorators import require_htmx
from helpers.filters import ModelSearchFilterBackend
from clients.views import \
        FormRequestMixin
from .models import Product, \
                    OrderProxy
from .forms import AddOrderForm, \
                    ProductForm


T = TypeVar("T", bound=QuerySet)


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
    permission_map = {
        # GET is accessible to every user.
        "POST": "{app_label}.add_{model_name}",
        "PUT": "{app_label}.change_{model_name}",
        "DELETE": "{app_label}.delete_{model_name}",
    }
    method_map = {
        "post": "add_product",
        "put": "change_product",
        "delete": "delete_product",
    }

    def get_template_names(self):
        
        if self.request.htmx:
            return ["products/partials/product_update.html"]
        
        assert self.template_name is not None
        assert isinstance(self.template_name, (str, list, tuple))
        
        if isinstance(self.template_name, str):
            return [self.template_name]
        return self.template_name

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

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.get_object()})
        return kwargs

    def get_object(self, queryset: T = None) -> Product:

        model = queryset.model if queryset is not None else None or self.get_queryset().model
        kwargs = {"pk": self.kwargs["pk"], "product_slug": self.kwargs["slug"]}
        obj = get_object_or_404(model, **kwargs)
        self.object = obj
        return obj
    
    def dispatch(self, request, *args, **kwargs):
        self.check_user_permission(request)
        return super().dispatch(request, *args, **kwargs)

    def delete_object(self, instance) -> None:
        instance.delete()

    def form_valid(self, form):
        form.save()
        self.object.refresh_from_db()
        return HttpResponseClientRedirect(self.object.get_absolute_url())

    def check_user_permission(self, request) -> NoReturn:
        
        user = request.user
        model = self.model or self.get_queryset().model
        permissions = self.perms(model)
        for method, perm in permissions.items():
            if request.method == method and not self.has_perm(user, perm):
                self.permission_denied()

    def has_perm(self, user, perm) -> bool:
        return user.is_authenticated and all([user.has_perm(perm), user.is_staff])

    @property
    def permissions(self):
        kw = {}
        user = self.request.user
        model = self.model
        method_map = self.method_map
        for key, perm in self.perms(model).items():
            method = method_map.get(key.lower())
            assert method is not None
            kw[method] = self.has_perm(user, perm)
        
        return kw

    @require_htmx
    @permission_required("products.delete_product")
    def product_delete_view(request, *args, **kwargs) -> HttpResponse:
        
        def get_object() -> Product:
            obj = get_object_or_404(Product, **kwargs)
            return obj
        
        if request.method in ("POST", "DELETE"):
            get_object().delete()
    
            return HttpResponseClientRedirect(reverse("products"))
        raise PermissionDenied()

    staticmethod(product_delete_view)

    def get_context_data(self, **kwargs):
        kwargs = {**self.permissions, **kwargs}
        return super().get_context_data(**kwargs)

    def perms(self, model_class: Any) -> dict[str, str]:
        opts = model_class._meta
        kwargs = {
            "app_label": opts.app_label,
            "model_name": opts.verbose_name
        }
        return {k: v.format(**kwargs) for (k, v) in self.permission_map.items()}

    def permission_denied(self):
        
        raise PermissionDenied()


@method_decorator(require_htmx, name="dispatch")
class ProductSearchView(View):

    filter_backends = [ModelSearchFilterBackend]

    def get_query_param(self, request) -> str:
        
        return getattr(self, "search_query", "q")

    def get(self, request: HttpRequest) -> HttpResponse:

        context = {}
        query = self.get_query_param(request)
        queryset = Product.objects.all()
        if query:
            queryset = self.filter_queryset(request, queryset).order_by("-timestamp")
        
        context["queryset"] = queryset

        return render(request, "products/partials/product_list.html", context)
    

    def filter_queryset(self, request, queryset: T) -> T:
        
        for filter in self._filters:
            queryset = filter.filter_queryset(request, queryset, self)
        return queryset

    @property
    def _filters(self):

        return [x() for x in self.filter_backends]


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
class ProductCreateView(FormRequestMixin,
                        PermissionRequiredMixin,
                        CreateView):

    template_name = "products/product_create.html"
    form_class = ProductForm
    model = Product
    permission_required = "%(app_name)s.add_%(model_name)s"

    def get_permission_required(self):
        opts = self.model._meta
        kwargs = {
            "app_name": opts.app_label,
            "model_name": opts.model_name

        }
        self.permission_required = self.permission_required % kwargs
        
        return super().get_permission_required()


    def get_context_data(self, **kwargs):
        kwargs["title"] = "Create Product"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


product_create_view = ProductCreateView.as_view()