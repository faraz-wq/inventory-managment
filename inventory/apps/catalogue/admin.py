# catalogue/admin.py
from django.contrib import admin
from .models import ItemInfo, ItemAttribute


class ItemAttributeInline(admin.TabularInline):
    model = ItemAttribute
    extra = 1


@admin.register(ItemInfo)
class ItemInfoAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'item_name', 'category', 'active']
    list_filter = ['category', 'resource_type', 'active']
    search_fields = ['item_code', 'item_name', 'tags']
    inlines = [ItemAttributeInline]  # This is where ItemAttribute belongs!


@admin.register(ItemAttribute)
class ItemAttributeAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_info', 'key', 'datatype']
    list_filter = ['datatype']
    search_fields = ['item__item_name', 'key']