from django.contrib import admin
from django.db.models import QuerySet

from .models import get_token_model


Token = get_token_model()


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):

    fields = ("user",)
    list_display = ("user__username", "created", "expired_at")
    search_fields = ["user__username", "key"]
    list_filter = ["created", "expired_at"]


    def get_queryset(self, request) -> QuerySet:

        return super().get_queryset(request).select_related("user")

