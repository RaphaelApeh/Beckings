from django.contrib.auth import get_user_model
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from products.models import Product


User = get_user_model()


class ProductResource(ModelResource):

    class Meta:
        model = "products.Product"
        fields = (
            "product_name",
            "product_description",
            "price",
            "active",
            "quantity"
        )
        import_id_fields = (
            "product_name",
            "product_description",
            "price",
            "active",
            "quantity"
        )
    
    def after_init_instance(self, instance, new, row, **kwargs):
        assert "user" in kwargs, "Forgot to pass in `user` argument"
        user = kwargs.pop("user")
        instance.user = user
        return super().after_init_instance(instance, new, row, **kwargs)


class OrderResource(ModelResource):

    product = Field(
        column_name="product",
        attribute="product",
        widget=ForeignKeyWidget(Product, field="product_name")
    )

    user = Field(
        column_name="user",
        attribute="user",
        widget=ForeignKeyWidget(User, field="username")
    )

    class Meta:
        model = "products.Order"
        fields = (
            "product",
            "user",
            "number_of_items",
            "status"
        )
    
