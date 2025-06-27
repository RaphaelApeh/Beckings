import django_filters

from .models import Product


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
    
