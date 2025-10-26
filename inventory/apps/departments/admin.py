"""
Departments Admin Configuration
"""
from django.contrib import admin
from .models import Department, DepartmentContact


class DepartmentContactInline(admin.TabularInline):
    model = DepartmentContact
    extra = 1


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'org_code', 'org_shortname', 'org_name', 'active']
    list_filter = ['active', 'org_type']
    search_fields = ['org_name', 'org_shortname', 'org_code']
    ordering = ['org_name']
    inlines = [DepartmentContactInline]


@admin.register(DepartmentContact)
class DepartmentContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'dept', 'contact_type', 'contact_value']
    list_filter = ['contact_type']
    search_fields = ['dept__org_name', 'contact_value']
