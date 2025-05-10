from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    list_display = ["product_name", "product_slug", "active"]
    prepopulated_fields = {"product_slug": ("product_name",)}
    fieldsets = (
        (None, {"fields": ("product_name", "user")}),
        ("Extra Data", {"fields": ("product_description", "price", "product_slug", "active")}),
        
    )