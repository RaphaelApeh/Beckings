from __future__ import annotations

import uuid
from typing import Any

from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from cloudinary.models import CloudinaryField

from helpers.fields import AutoSlugField
from helpers.enum import OrderStatusChoices
from .manager import ProductManager


User = get_user_model()


class Product(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_products",
    )
    product_name = models.CharField(max_length=100, db_index=True)
    product_description = models.TextField(null=True, blank=True)
    product_slug = AutoSlugField(
        perform_from="product_name", blank=True, null=True, db_index=True
    )
    price = models.FloatField(default=1000.0)
    image = CloudinaryField("image", blank=True, null=True)
    active = models.BooleanField(default=True)
    quantities = None
    quantity = models.PositiveSmallIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    out_of_stock = models.GeneratedField(
        expression=models.Case(
            models.When(quantity__lte=0, then=True),
            default=False,
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )
    comments = GenericRelation("comment")

    SEARCH_FIELDS = ("product_name", "product_description", "price")

    def __str__(self) -> str:
        return self.product_name

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["product_name"], name="product_name_index")]
        permissions = (("user_product", _("User Add/Update/Delete Product")),)

    objects = ProductManager()

    def get_absolute_url(self) -> str:

        return reverse(
            "product-detail", kwargs={"pk": self.pk, "slug": self.product_slug}
        )


def create_product(**kwargs: Any) -> Product:
    return Product.objects.create(**kwargs)


# for testing purposes


def create_bulk_product(args: list[dict[str, Any]]) -> list[Product]:
    return [create_product(**x) for x in args]


ORDER_CHOICES = {
    "delivered": _("Delivered"),
    "pending": _("Pending"),
    "cancelled": _("Cancelled"),
}


class Order(models.Model):

    order_id = models.UUIDField(
        primary_key=True, verbose_name=_("Order ID"), default=uuid.uuid1, editable=False
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("User")
    )

    manifest = models.TextField(blank=True, null=True, verbose_name=_("Manifest"))

    number_of_items = models.PositiveSmallIntegerField(default=0)
    inactive_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=OrderStatusChoices.choices, default="pending"
    )

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self) -> str:

        return "{id} - {name}".format(id=self.order_id, name=self.__class__.__name__)

    def can_delete(self):
        return ("pending",)

    def cancel(self):
        self.status = "cancelled"
        self.inactive_at = now()
        self.save()


class OrderProxy(Order):

    class Meta:
        proxy = True
        verbose_name = _("User Order")
        verbose_name_plural = _("User Orders")

    def cancelled(self) -> bool:
        return self.status == "cancelled"

    cancelled.short_description = _("Cancelled")


class Comment(models.Model):

    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "comments"
        indexes = (models.Index(fields=("message",)),)
        ordering = ("-timestamp",)


class Reply(models.Model):

    comment = models.ForeignKey(
        Comment, related_name="replies", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        indexes = (models.Index(fields=("message",)),)
        verbose_name_plural = _("Replies")
