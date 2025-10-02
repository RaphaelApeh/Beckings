from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import FeedBack


@admin.register(FeedBack)
class FeedBackAdmin(ModelAdmin):
    list_display = ("email", "complain_type", "resolved", "timestamp")    
    list_filter = ("resolved", "complain_type")
    search_fields = ("email", "complain")