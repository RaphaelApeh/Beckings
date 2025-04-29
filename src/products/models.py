import uuid

from django.db import models


class Product(models.Model):

    id = models.UUIDField(primary_key=True, db_default=uuid.uuid1(), editable=False)
    product_name = models.CharField(max_length=100)
    product_slug = models.SlugField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    timpstamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product_name
