# items/admin.py - CORRECTED
from django.contrib import admin
from .models import Item, ItemAttributeValue  # Import the correct model


class ItemAttributeValueInline(admin.TabularInline):
    model = ItemAttributeValue
    extra = 1
    # Optional: make it more user-friendly
    autocomplete_fields = ['item_attribute']


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
    inlines = [ItemAttributeValueInline]  # Use the corrected inline

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


# This should probably be in catalogue/admin.py, not items/admin.py
@admin.register(ItemAttributeValue)  # Register the correct model
class ItemAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'item_attribute', 'value']
    list_filter = ['item_attribute__datatype']
    search_fields = ['item__iteminfo__item_name', 'item_attribute__key', 'value']