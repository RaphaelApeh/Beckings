from django.urls import path

from .views import (ProductListView, 
                    ProductDetailView,
                    product_search_view)


urlpatterns = [

    path("", ProductListView.as_view(), name="products"),

    path("<int:pk>/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    path("search/", product_search_view, name="product_search")
]
