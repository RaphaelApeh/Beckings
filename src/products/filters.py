import django_filters

from .models import Product

class ProductFilterSet(django_filters.FilterSet):

    price = django_filters.RangeFilter("price")

    class Meta:
        model = Product 
        fields = {
            "product_name": ["iexact", "icontains"],
            "product_description": ["iexact", "icontains"],
            "price": ["lte", "gte"],
            "quantity": ["lte", "gte"]
        }
    
