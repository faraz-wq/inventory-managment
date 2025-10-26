"""
Catalogue Admin Configuration
"""
from django.contrib import admin
from .models import ItemInfo


@admin.register(ItemInfo)
class ItemInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_code', 'item_name', 'category', 'unit', 'active']
    list_filter = ['active', 'category', 'resource_type', 'perishability']
    search_fields = ['item_name', 'item_code', 'category', 'tags']
    ordering = ['item_name']
