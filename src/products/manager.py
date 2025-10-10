from django.db import models
from django.contrib.postgres.search import SearchVector


class ProductManager(models.Manager):

    def search(self, query: str | None = None) -> models.QuerySet:

        search_fields = getattr(self.model, "SEARCH_FIELDS", ())

        if not search_fields:
            return self.none()

        _search = SearchVector(search_fields)

        return self.annotate(search=_search).filter(search=query)

    def active(self):
        return self.filter(active=True)


class OrderManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().annotate(
            total_cost=models.F("product__price") * models.F("number_of_items")
        )

