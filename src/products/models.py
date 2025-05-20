from __future__ import annotations

from typing import Any

from cloudinary import CloudinaryImage
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from helpers import init_cloudinary
from .manager import ProductManager


User = get_user_model()


init_cloudinary()

class Product(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_products")
    product_name = models.CharField(max_length=100)
    product_description = models.TextField(null=True, blank=True)
    product_slug = models.SlugField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=1000.0)
    image = CloudinaryImage()
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    SEARCH_FIELDS = ("product_name", "product_description", "price")

    def __str__(self) -> str:
        return self.product_name

    objects = ProductManager()

    def get_absolute_url(self) -> str:

        return reverse("product-detail", kwargs={"pk": self.pk, "slug": self.product_slug})
    

    def save(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        self.product_slug = slugify(self.product_name)
        super().save(*args, **kwargs)
