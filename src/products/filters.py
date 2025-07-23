import django_filters

from .models import (
    Product,
    Order,
    ORDER_CHOICES
)


TIMESTAMP_CHOICES = (
    ("", "-------"),
    ("today", "Today"),
    ("yesterday", "Yesterday",),
    ("last_week", "Last Week"),
    ("last_month", "Last Month"),
    ("three_months" "3 Months Ago"),
    ("last_year", "Last Year")
)

class ProductFilter(django_filters.FilterSet):

    price = django_filters.RangeFilter("price")

    class Meta:
        model = Product 
        fields = (
            "product_name",
            "product_description",
            "price",
            "quantity"
        )
    

class OrderFilter(django_filters.FilterSet):

    status = django_filters.ChoiceFilter(
        choices=ORDER_CHOICES,
        label="Status"
    )
    timestamp = django_filters.ChoiceFilter(
        choices=TIMESTAMP_CHOICES,
        label="Date"
    )

    class Meta:
        model = Order
        fields = ["status"]
