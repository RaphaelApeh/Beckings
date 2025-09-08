from __future__ import annotations

from typing import Any, TypeVar, NoReturn

from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.db.models import QuerySet
from django.forms import (
    modelformset_factory, 
    ModelForm
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    ListView,
    DetailView,
    FormView,
    CreateView
    )
from django.views.generic.edit import FormMixin
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import ModelFormMixin, DeletionMixin
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required

from django_filters.views import FilterView
from django_htmx.http import HttpResponseClientRedirect

from helpers.decorators import require_htmx
from helpers._typing import HTMXHttpRequest
from helpers.forms.mixins import TailwindRenderFormMixin
from clients.views import FormRequestMixin
from .models import (
    Product,
    Order, 
    Comment, 
    Reply
)
from .forms import (
    AddOrderForm, 
    ProductForm,
    ExportForm,
    CommentForm,
    ReplyForm,
    SearchForm
)
from .filters import (
    ProductFilter,
    OrderFilter
)


login_required_m = method_decorator(login_required, name="dispatch")
require_htmx_m = method_decorator(require_htmx, name="dispatch")
never_cache_m = method_decorator(never_cache, name="dispatch")

T = TypeVar("T", bound=QuerySet)
QUERY_SEACRH = "search"


class ObjectUserCheckMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


@never_cache_m
class ProductListView(ListView):

    queryset = Product.objects.select_related("user").filter(active=True)
    template_name = "products/product_list.html"
    context_object_name = "queryset"
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            return (
                "helpers/products/object_list.html",
            )
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        kwargs.update({
            "search_form": SearchForm()
        })
        return super().get_context_data(**kwargs)


class ProductDetailView(FormRequestMixin, 
                        ModelFormMixin, 
                        DetailView):
    http_method_names = (
        "get",
        "post",
        "put",
        "delete"
    )
    queryset = (
        Product.objects.prefetch_related(
            "comments", 
            "comments__replies"
        ).select_related("user")
    )
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

    def form_valid(self, request: HttpRequest, form):
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
        model = self.get_queryset().model
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
class ProductSearchView(FilterView):

    ordering =  ("-timestamp",)
    template_name = (
        "helpers/products/search.html"
    )
    filterset_class = ProductFilter
    
    def get_filterset_data(self, request: HttpRequest, filter_class) -> dict:

        data = dict.fromkeys(
            (filter_class.base_filters.keys()),
            request.GET[QUERY_SEACRH]
        )
        
        return data
    
    def get_filterset_kwargs(self, filterset_class):
        
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs.update(
            {
                "data": self.get_filterset_data(self.request, filterset_class)
            }
        )
        return kwargs


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
                "order_form": OrderFilter().form,
                "export_form": ExportForm(auto_id=False)
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
        if request.htmx:
            return self.htmx_get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)
    
    def htmx_get(self, request, *args, **kwargs):
        qs = self.get_queryset()
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
    
    def get_order_action_choices(self, request):
        return None

user_orders_view = UserOrderView.as_view()


@login_required_m
class UserOrderDetailView(DetailView):

    model = Order
    pk_url_kwarg = "order_id"
    template_name = "helpers/orders/object.html"

    def post(self, request, *args, **kwargs):
        if request.htmx:
            obj = self.get_object()
            with transaction.atomic():
                obj = self._cancel_user_order(request, obj)
            return self.render_to_response(context=self.get_context_data(object=obj))
        return HttpResponse(status=204) # NO CONENT

    def _cancel_user_order(self, request, obj):
        obj.status = "cancelled"
        obj.save()
        self.object = obj
        return obj


@method_decorator((login_required, require_htmx), name="dispatch")
class AddOrderView(
    SingleObjectMixin,
    FormRequestMixin, 
    FormView
    ):

    template_name = "orders/add_order.html"
    form_class = AddOrderForm
    model = Product # for form field
    object = None
    pk_url_kwarg = "product_id"

    def get_form_kwargs(self) -> dict[str, Any]:
        kw = super().get_form_kwargs()
        kw.setdefault("view", self)
        kw["initial"] = self.get_form_initial(self.request, None, None)
        return kw
    
    def get_form_initial(self, request, obj, form):
        kwargs = {}
        kwargs["product"] = self.get_object()
    
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        obj = form.save()
        self.object = obj.product
        return HttpResponseClientRedirect(obj.product.get_absolute_url())


@never_cache_m
@login_required_m
class OrderExportView(
    FormMixin,
    View
    ):

    form_class = ExportForm
    queryset = Order.objects.select_related("user", "product")


    def get_queryset(self) -> QuerySet:
        if self.queryset:
            return self.queryset.filter(user=self.request.user)
        elif getattr(self, "model", None) is not None:
            return self.model._default_manager.filter(user=self.request.user)
        raise AttributeError(
            "get_queryset() method required"
            "queryset or model attribute"
        )

    def get(self, request) -> HttpResponse:
        if request.htmx:
            return HttpResponseClientRedirect(
                request.get_full_path()
            )
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


    def form_valid(self, form) -> HttpResponse:
        qs = self.get_queryset()
        model = qs.model
        object_name = model._meta.object_name
        format, export_data = form.export_data(self.request, qs)
        response = (
            HttpResponse(
                export_data, 
                content_type=format.get_content_type()
            )
        )
        response["Content-Disposition"] = (
            'attachment; filename="{}"'.format(
                form.date_format(format, object_name)
                )
        )
        return response
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.method == "GET":
            kwargs.update(
                {
                    "data": self.request.GET or None,
                    "files": self.request.FILES or None
                }
            )
        return kwargs


export_order_view = OrderExportView.as_view()


@login_required_m
@require_htmx_m
class UserOrderDeleteView(
    SingleObjectMixin,
    ObjectUserCheckMixin,
    View
):
    queryset = (
        Order.objects.select_related("user", "product")
    )
    pk_url_kwarg = "order_id"

    def get_queryset(self):
        return (
            super().get_queryset().filter(user=self.request.user)
        )
    
    def delete(self, request: HTMXHttpRequest, *args, **kwargs):

        user = request.user
        prompt = request.htmx.prompt
        self.object = obj = self.get_object()
        if user.check_password(prompt):
            obj.delete()
            return HttpResponse(status=204)
        raise Http404

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


@method_decorator(staff_member_required(login_url="login"), name="dispatch")
class ProductCreateView(
    PermissionRequiredMixin,
    CreateView
    ):

    template_name = "products/product_create.html"
    model = Product
    class _ProductForm(TailwindRenderFormMixin, ModelForm):

        class Meta:
            model = Product
            fields = [
            "product_name",
            "product_description",
            "price",
            "quantity",
            "active"
        ]
    form_class = _ProductForm
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
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            formset=self.get_form(),
            form=None
        )
        return kwargs

    def form_valid(self, formset):
        request = self.request
        saved_objs = set()
        total_objs = len(formset.cleaned_data)
        deleted_objs = len([data for data in formset.cleaned_data if data.get("DELETE")])
        skipped = 0
        for form in formset:
            if form.is_valid() and not form.cleaned_data.get("DELETE", False):
                obj = form.save()
                saved_objs.add(obj)
            else:
                skipped += 1
        msg = f"Saved {len(saved_objs)} Item(s), Total {total_objs} Item(s), Skipped {skipped} Item(s), Deleted {deleted_objs} Item(s)."
        if skipped > len(saved_objs):
            messages.warning(request, msg)
        elif not len(saved_objs) and deleted_objs:
            messages.error(request, msg)
        else:
            messages.success(self.request, msg)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return self.request.path
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        qs = self.get_queryset().none()
        kwargs.setdefault("queryset", qs)
        kwargs.pop("instance", None)
        return kwargs
    
    def get_form_class(self):
        model = self.get_queryset().model
        assert hasattr(self, "form_class") and self.form_class is not None
        return (
            modelformset_factory(
                model,
                extra=0,
                form=self.form_class,
                fields=self.form_class._meta.fields,
                exclude=self.form_class._meta.exclude,
                can_delete=True,
                max_num=5
            )
        )
    


product_create_view = ProductCreateView.as_view()


# Comments

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
    pk_url_kwarg = "reply_id"

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

