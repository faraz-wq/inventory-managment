from django.contrib import admin
from .models import BorrowRecord


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['borrower_name', 'item', 'phone_number', 'department', 'status', 'borrow_date', 'expected_return_date']
    list_filter = ['status', 'borrow_date', 'department', 'location']
    search_fields = ['borrower_name', 'aadhar_card', 'phone_number', 'item__iteminfo__item_name']
    date_hierarchy = 'borrow_date'
    readonly_fields = ['created_at', 'updated_at', 'borrow_date']

    fieldsets = (
        ('Item Information', {
            'fields': ('item', 'status')
        }),
        ('Borrower Personal Details', {
            'fields': ('borrower_name', 'aadhar_card', 'phone_number', 'address')
        }),
        ('Borrower Organizational Details', {
            'fields': ('department', 'location')
        }),
        ('Borrow Details', {
            'fields': ('borrow_date', 'expected_return_date', 'actual_return_date', 'borrow_notes', 'return_notes')
        }),
        ('Processing Information', {
            'fields': ('issued_by', 'received_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
