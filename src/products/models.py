import uuid

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Product(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_products")
    product_name = models.CharField(max_length=100)
    product_description = models.TextField(null=True, blank=True)
    product_slug = models.SlugField(blank=True, null=True)
    price = models.FloatField(default=1000.0)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    timpstamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product_name
