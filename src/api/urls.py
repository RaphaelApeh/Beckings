from django.urls import path
from rest_framework.routers import DefaultRouter

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from .views import (
    UserAPIView,
    ProductListCreateView,
    ProductRetrieveView,
    TokenLoginAPIView,
    ChangePasswordAPIView,
    TokenLogoutAPIView,
    UserOrderListAPIView,
    UserOrderRetrieveAPIView,
    )


urlpatterns = [
    path("login/", TokenLoginAPIView.as_view(), name="api_login"),
    path("logout/", TokenLogoutAPIView.as_view(), name="api_logout"),

    path("users/change-password/", ChangePasswordAPIView.as_view(), name="api_user_change_password"),
    
    # products Views
    path("products/", ProductListCreateView.as_view(), name="product_list"),
    path("products/<pk>/<product_slug>/", ProductRetrieveView.as_view(), name="product_retrieve"),

    # DRF Spectacular
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # User Orders
    path("orders/", UserOrderListAPIView.as_view(), name="user_order"),
    path("orders/<uuid:order_id>/", UserOrderRetrieveAPIView.as_view(), name="order_retrieve")
]


router = DefaultRouter()

router.register("users", UserAPIView)

urlpatterns += router.urls

