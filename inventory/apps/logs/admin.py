"""
Logs Admin Configuration
"""
from django.contrib import admin
from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject_type', 'subject_id', 'action', 'status', 'created_at']
    list_filter = ['subject_type', 'action', 'status', 'created_at']
    search_fields = ['user__name', 'user__email', 'subject_type', 'action']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        """Logs are created automatically, prevent manual creation"""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs should not be modified"""
        return False
