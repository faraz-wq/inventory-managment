"""
Items Admin Configuration
"""
from django.contrib import admin
from .models import Item, ItemAttribute


class ItemAttributeInline(admin.TabularInline):
    model = ItemAttribute
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'iteminfo', 'dept', 'status', 'geocode',
        'created_by', 'verified_by', 'created_at'
    ]
    list_filter = ['status', 'dept', 'geocode__district', 'iteminfo__category']
    search_fields = [
        'iteminfo__item_name', 'iteminfo__item_code',
        'operational_notes', 'dept__org_name'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ItemAttributeInline]

    fieldsets = (
        ('Item Information', {
            'fields': ('iteminfo', 'photo', 'eol_date', 'operational_notes', 'status')
        }),
        ('Organization & Location', {
            'fields': ('dept', 'geocode', 'latitude', 'longitude')
        }),
        ('User Information', {
            'fields': ('user', 'created_by', 'verified_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemAttribute)
class ItemAttributeAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'key', 'value', 'datatype']
    list_filter = ['datatype']
    search_fields = ['item__iteminfo__item_name', 'key', 'value']
