from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import Client


@admin.register(Client)
class ClientAdmin(ModelAdmin):

    list_display = ("user__username", "phone_number")
    list_filter = ("phone_number",)
    search_fields = (
        "user__username",
        "phone_number",
        "address"
    )