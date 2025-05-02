from typing import final
from typing import Any

from django.db.models import QuerySet
from django.contrib.syndication.views import Feed

from products.models import Product


@final
class ProductFeed(Feed):

    
    def title(self, obj: Any=None) -> str:
        return "Hello World"

    def link(self, obj) -> str:
        return "/products/"
    
    def items(self) -> QuerySet:
        return Product.objects.order_by("-timpstamp")[:50]
    
    def item_title(self, item: type[Product]):
        return item.product_name
    
    def item_description(self, item: type[Product]):
        return item.product_description
    
