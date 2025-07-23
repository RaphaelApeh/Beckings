from __future__ import annotations

import hashlib
from typing import Any, Optional, TypeVar, NoReturn

from faker import Faker
from tablib import Dataset
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
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
from django.http import (
                        Http404,
                        HttpRequest,
                        HttpResponse,
                        HttpResponseBadRequest,
                        HttpResponseRedirect,
                        )
from django.http.response import HttpResponseBase
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import ModelFormMixin, DeletionMixin
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required

from django_htmx.http import HttpResponseClientRedirect

from helpers.decorators import require_htmx
from helpers.filters import ModelSearchFilterBackend
from helpers.resources import ProductResource
from clients.views import \
        FormRequestMixin
from .models import Product, \
                    Order, Comment, Reply #noqa
from .forms import AddOrderForm, \
                    ProductForm, \
                    ProductImportForm, \
                    ExportForm, \
                    CommentForm, \
                    ReplyForm
from .filters import (
    OrderFilter
)


login_required_m = method_decorator(login_required, name="dispatch")
require_htmx_m = method_decorator(require_htmx, name="dispatch")

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
            return self.form_valid(request, form)
        return self.form_invalid(request, form)
    
    def form_invalid(self, request, form):
        return super().form_invalid(form)
    
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

    def form_valid(self, request, form):
        form.save()
        self.object.refresh_from_db()
        messages.success(request, "Object Save")
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
        instance = get_object()
        if request.method in ("POST", "DELETE"):
            messages.success(request, "%s deleted successfully" % instance)
            with transaction.atomic():
                instance.delete()
    
            return HttpResponseClientRedirect(reverse("products"))
        raise PermissionDenied()

    staticmethod(product_delete_view)

    def get_context_data(self, **kwargs):
        kwargs = {**self.permissions, **kwargs}
        kwargs["export_form"] = ExportForm()
        kwargs["comment_form"] = (
            CommentForm(**self.get_comment_form_initial_kwargs(self.request))
        )
        return super().get_context_data(**kwargs)

    def perms(self, model_class: Any) -> dict[str, str]:
        opts = model_class._meta
        kwargs = {
            "app_label": opts.app_label,
            "model_name": opts.verbose_name
        }
        return {k: v.format(**kwargs) for (k, v) in self.permission_map.items()}

    def get_comment_form_initial_kwargs(self, request, **kwargs):
        
        kwargs.setdefault("initial", {
            "product_id": self.get_object().pk
        })
        return kwargs

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


@login_required_m
class UserOrderView(ListView):

    queryset = Order.objects.select_related("user", "product")   
    template_name = "orders/order_list.html"
    allow_empty = False
    filter_class = OrderFilter

    def get_queryset(self) -> T:
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "order_form": OrderFilter().form
            }
        )
        return context
    
    def get_filter_class(self, request):

        return self.filter_class
    
    
    def get_filter_instance(self, data, request, queryset):

        _filter = self.get_filter_class(request)
        return _filter(data, queryset, request=request)
    

    def filter(self, data, request, queryset):
        
        self._filter = self.get_filter_instance(data, request, queryset)
        return self._filter


    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if request.htmx:
            form = self.filter(request.GET or None, request, qs)
            if not form.is_valid():
                qs = qs.all()
                return render(
                    request, 
                    "helpers/orders/object_list.html",
                    {"object_list": qs}) 
            qs = form.qs
            return render(
                request, 
                "helpers/orders/object_list.html", 
                {"object_list": qs})
        return super().get(request, *args, **kwargs)
    

    def get_order_action_choices(self, request):
        return None

user_orders_view = UserOrderView.as_view()


@method_decorator((login_required, require_htmx), name="dispatch")
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
        kw.update({"auto_id": False})
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
        kwargs["import_form"] = ProductImportForm(initial={"format": "csv"})
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = instance = form.save()
        messages.success(self.request, "%s created success" % instance)
        return HttpResponseRedirect(self.get_success_url())


product_create_view = ProductCreateView.as_view()


@method_decorator(never_cache, name="dispatch")
class ProductExportImportView(View):

    mapping = {
            "json": {
                "type": lambda x: x.json, 
                "content-type": "application/json"
            },
            "csv": {
                "type": lambda x: x.csv, 
                "content-type": "text/csv"
            },
            "yaml": {
                "type": lambda x: x.yaml, 
                "content-type": "text/yaml"
            },
            "html": {
                "type": lambda x: x.html,
                "content-type": "text/html",
            }
    }

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs) -> HttpResponse:

        mapping = self.mapping
        ids = request.GET.getlist("id")
        queryset = self.get_queryset().filter(pk__in=ids)
        form = ExportForm(request.GET or None)

        export = self.export_data(request, queryset)
        
        if form.is_valid():
            format = form.cleaned_data["format"]
        ds = mapping.get(format)

        hash = self.hash()
        response = HttpResponseBadRequest(content="Error")
        
        if (type_ := ds.get("type")) is not None:
            response = HttpResponse(type_(export), content_type=ds.get("content-type", None))
        
            response["Content-Disposition"] = f'attachment; filename="product_{hash}.{format}"'
        
        return response
    
    def hash(self) -> str:
        
        _s = Faker().sentence(5).encode()
        
        return hashlib.md5(_s).hexdigest()
    
    def export_data(self, request, queryset: T | None = None) -> Any:
        if not len(list(queryset)):
            queryset = None
        ds = ProductResource.export_data(queryset)
        return ds
    
    def import_data(self, request, form, queryset: T) -> Any:
        
        resource = ProductResource()
        user = request.user
        ds = Dataset()

        if form.is_valid():
            file = form.cleaned_data["file"]
            _file_data = ds.load(file.read().decode())
            import_data = resource.import_data(_file_data, user=user, dry_run=True)
            for row in import_data:
                for error in row.errors:
                    print(error)
            if not import_data.has_errors():
                import_data = resource.import_data(_file_data, dry_run=False, user=user)
        next_url = request.META.get("HTTP_REFERER") or reverse("products")
        return HttpResponseRedirect(next_url)

    def get_queryset(self):
        return Product.objects.select_related("user")

    @method_decorator(staff_member_required(login_url="login"))
    def post(self, request, *args, **kwargs):
        
        queryset = self.get_queryset()
        
        form = ProductImportForm(data=request.POST or None, files=request.FILES or None)
        
        next_url = request.META.get("HTTP_REFERER") or reverse("products")
        response = HttpResponseRedirect(next_url)

        if not form.is_valid():
            messages.error(request, "An Error orcured.")
            return response
        format = form.cleaned_data["format"]

        file = form.cleaned_data["file"]
        if not file.name.endswith(f".{format}"):
            messages.error(request, "Invalid Format.")
            return response

        with transaction.atomic():
            messages.success(request, "Data Saved.")
            result = self.import_data(request, form, queryset)
            if isinstance(result, HttpResponseBase):
                return result
        return response


export_import_product_view = ProductExportImportView.as_view()

# Comments

class ObjectUserCheckMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

@require_htmx_m
@login_required_m
class CommentCreateView(
    SingleObjectMixin,
    FormView):

    model = Product
    form_class = (
        CommentForm
    )
    template_name = "helpers/comments/object.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        
        kwargs = {}
        data = form.cleaned_data
        object = Comment.objects.create(
            user=self.request.user,
            content_object=self.get_object(),
            message=data.get("message")
        )
        kwargs["comment"] = object
        return self.render_to_response(self.get_context_data(**kwargs))


@login_required_m
@require_htmx_m
class CommentDeleteView(
    SingleObjectMixin,
    ObjectUserCheckMixin,
    DeletionMixin,
    View):
    model = Comment
    pk_url_kwarg = "comment_id"
    success_url = "/"


@login_required_m
@require_htmx_m
class CommentUpdateView(
    SingleObjectMixin,
    ObjectUserCheckMixin,
    FormView
):
    model = Comment
    form_class = CommentForm
    template_name = "helpers/comments/update.html"
    pk_url_kwarg = "comment_id"

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        obj = self.get_object()
        context.update(
            {
                "initial": self.get_form_initial(self.request, obj)
            }
        )
        return context
    
    def get_form_initial(self, request, obj):
        return {
            "product_id": obj.object_id,
            "message": obj.message
        }
    
    def form_valid(self, form):

        obj = self.get_object()

        with transaction.atomic():
            self.object = self._save_object(self.request, form, obj)
        return render(
            self.request,
            "helpers/comments/object.html",
            self.get_context_data()
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "object": Product.objects.get(id=self.object.object_id),
                "comment": self.object,
                "comment_form": self.get_form()
            }
        )
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def _save_object(self, request, form, obj):

        obj.message = form.cleaned_data["message"]
        obj.save()
        return obj


@login_required_m
@require_htmx_m
class ReplyView(
    SingleObjectMixin,
    FormView):

    model = Comment
    template_name = "helpers/replies/form.html"
    pk_url_kwarg = "comment_id"
    form_class = ReplyForm
    object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        obj = self.get_object()
        kwargs.update(
            {
                "initial": self.get_form_initial(self.request, obj)
            }
        )
        return kwargs
    
    def get_form_initial(self, request, obj):
        kwargs = {}
        kwargs["comment_id"] = obj.pk 
        kwargs["redirect_url"] = request.META["HTTP_REFERER"]
        return kwargs

    def form_valid(self, form):
        
        obj = self.get_object()
        
        with transaction.atomic():
            self.object = self._create_reply(
                self.request, form, obj
            )
        url = self.request.META["HTTP_REFERER"]
        return HttpResponseClientRedirect(url)
    
    def _create_reply(self, request, form, obj):

        Reply.objects.create(
            user=request.user,
            comment=obj,
            message=form.cleaned_data["message"]
        )
        return obj


@login_required_m
@require_htmx_m
class ReplyDeleteView(
    DeletionMixin,
    SingleObjectMixin,
    ObjectUserCheckMixin,
    View
):
    model = Reply
    pk_url_kwarg = "reply_id"

    def get_success_url(self):
        return self.request.META["HTTP_REFERER"]


@login_required_m
@require_htmx_m
class ReplyUpdateView(
    SingleObjectMixin,
    ObjectUserCheckMixin,
    FormView
):

    form_class = ReplyForm
    model = Reply
    template_name = "helpers/replies/form.html"
    object = None

    def form_valid(self, form):
        
        with transaction.atomic():
            self.object = self._save_reply_object(self.request, self.get_object(), form)
        
        return HttpResponseClientRedirect(
            self.get_success_url()
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "initial": self.get_form_initial(self.request, self.get_object())
            }
        )
        return kwargs

    def get_form_initial(self, request, obj):

        return {
            "comment_id": obj.comment_id,
            "redirect_url": self.get_success_url(),
            "message": obj.message
        }

    def get_success_url(self):
        return self.request.META["HTTP_REFERER"]

    def _save_reply_object(self, request, obj, form):

        message = form.cleaned_data["message"]
        obj.message = message
        obj.save()
        return obj

