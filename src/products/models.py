from __future__ import annotations

import uuid
from typing import Any

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from cloudinary import CloudinaryImage #noqa

from .manager import ProductManager


User = get_user_model()


class Product(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_products")
    product_name = models.CharField(max_length=100)
    product_description = models.TextField(null=True, blank=True)
    product_slug = models.SlugField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=1000.0)
    # image = CloudinaryImage("image")
    active = models.BooleanField(default=True)
    quantities = None
    quantity = models.PositiveSmallIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    out_of_stock = (
        models.GeneratedField(
            expression=models.Case(
                models.When(
                    quantity__lte=0, then=True
                ),
                default=False,
                output_field=models.BooleanField()
            ),
            output_field=models.BooleanField(),
            db_persist=True
        )
    )

    SEARCH_FIELDS = ("product_name", "product_description", "price")

    def __str__(self) -> str:
        return self.product_name

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["product_name"], name="product_name_index")
        ]


    objects = ProductManager()

    def get_absolute_url(self) -> str:

        return reverse("product-detail", kwargs={"pk": self.pk, "slug": self.product_slug})
    

    def save(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        self.product_slug = slugify(self.product_name)
        super().save(*args, **kwargs)


def create_product(**kwargs: Any) -> Product:
    return Product.objects.create(**kwargs)


# for testing purposes

def create_bulk_product(args: list[dict[str, Any]]) -> list[Product]:
    return [create_product(**x) for x in args]


ORDER_CHOICES = {

    "delivered": _("Delivered"),

    "pending": _("Pending"),
    
    "cancelled": _("Cancelled")
}


class Order(models.Model):

    order_id = models.UUIDField(primary_key=True,
                                verbose_name=_("Order ID"), 
                                default=uuid.uuid1,
                                editable=False)
    
    product = models.ForeignKey(Product, 
                                on_delete=models.CASCADE,
                                verbose_name=_("Product"))
    
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             verbose_name=_("User"))
    
    manifest = models.TextField(blank=True, 
                                null=True,
                                verbose_name=_("Manifest"))
    
    number_of_items = models.PositiveSmallIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_CHOICES, default="pending")


    def __str__(self) -> str:

        return "{id} - {name}".format(id=self.order_id, name=self.__class__.__name__)



class OrderProxy(Order):

    class Meta:
        proxy = True
        verbose_name = _("User Order")
        verbose_name_plural = _("User Orders")
    
    
    def cancelled(self) -> bool:
        return self.status == "cancelled"

    cancelled.short_description = _("Cancelled")
