from django.urls import path

from .views import (ProductListView, 
                    ProductDetailView,
                    product_search_view,
                    AddOrderView,
                    product_create_view,
                    user_orders_view,
                    export_import_product_view,
                    CommentDeleteView,
                    CommentCreateView,
                    CommentUpdateView,
                    ReplyView
                    )


urlpatterns = [

    path("", ProductListView.as_view(), name="products"),

    path("<int:pk>/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    path("search/", product_search_view, name="product_search"),

    path("delete/<int:pk>/<slug:product_slug>/",
         ProductDetailView.product_delete_view,
         name="product_delete"),

    path("create/", product_create_view, name="product_create"),

    path("export/", export_import_product_view, name="export_import_product"),

    # Orders Path
    path("orders/", user_orders_view, name="user_orders"),

    path("orders/add/<int:product_id>/", 
        AddOrderView.as_view(), 
        name="add_user_order"),

    path(
        "comment/add/<int:pk>/", 
        CommentCreateView.as_view(),
        name="add_comment"
        ),
    
    path(
        "comment/delete/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="delete_comment"
    ),
    path(
        "comment/update/<int:comment_id>/",
        CommentUpdateView.as_view(),
        name="update_comment"
    ),

    path(
        "replies/<int:comment_id>/",
        ReplyView.as_view(),
        name="reply"
    ),
]
