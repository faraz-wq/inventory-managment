from django.contrib import admin
from .models import BorrowRecord


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['borrower', 'get_borrower_email', 'item', 'status', 'borrow_date', 'expected_return_date']
    list_filter = ['status', 'borrow_date', 'borrower__dept', 'borrower__location']
    search_fields = ['borrower__name', 'borrower__email', 'borrower__phone_no', 'item__iteminfo__item_name']
    date_hierarchy = 'borrow_date'
    readonly_fields = ['created_at', 'updated_at', 'borrow_date', 'get_borrower_phone', 'get_borrower_department']

    def get_borrower_email(self, obj):
        return obj.borrower.email if obj.borrower else '-'
    get_borrower_email.short_description = 'Borrower Email'

    def get_borrower_phone(self, obj):
        return obj.borrower.phone_no if obj.borrower else '-'
    get_borrower_phone.short_description = 'Borrower Phone'

    def get_borrower_department(self, obj):
        return obj.borrower.dept.org_shortname if obj.borrower and obj.borrower.dept else '-'
    get_borrower_department.short_description = 'Department'

    fieldsets = (
        ('Item Information', {
            'fields': ('item', 'status')
        }),
        ('Borrower Information', {
            'fields': ('borrower', 'get_borrower_phone', 'get_borrower_department')
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
