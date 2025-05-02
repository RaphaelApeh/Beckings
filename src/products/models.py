from __future__ import annotations

from typing import Any

from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model


User = get_user_model()


class Product(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_products")
    product_name = models.CharField(max_length=100)
    product_description = models.TextField(null=True, blank=True)
    product_slug = models.SlugField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=1000.0)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    timpstamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product_name


    def get_absolute_url(self) -> str:

        return reverse("product-detail", kwargs={"pk": self.pk, "slug": self.product_slug})
    

@receiver(models.signals.pre_save, sender=Product)
def auto_slugify_product(sender: Product, instance: type[Product], **kwargs: dict[str, Any]) -> None:
    
    value = slugify(instance.product_name)[:10]
    prefix = ""
    if Product.objects.filter(product_slug=value).exists():
        prefix = get_random_string(5)
    instance.product_slug = slugify(f"{value}{prefix}".strip())


