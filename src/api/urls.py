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
    ChangePasswordAPIView
    )


urlpatterns = [
    path("login/", TokenLoginAPIView.as_view(), name="api_login"),

    path("users/change-password/", ChangePasswordAPIView.as_view()),
    
    # products Views
    path("products/", ProductListCreateView.as_view(), name="product_list"),
    path("products/<pk>/<product_slug>/", ProductRetrieveView.as_view(), name="product_retrieve"),

    # DRF Spectacular
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc")
]


router = DefaultRouter()

router.register("users", UserAPIView)

urlpatterns += router.urls

