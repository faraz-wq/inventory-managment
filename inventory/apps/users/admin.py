"""
Users Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['staff_id', 'email', 'name', 'dept', 'verified_status', 'active', 'created_at']
    list_filter = ['active', 'verified_status', 'dept', 'is_staff', 'is_superuser']
    search_fields = ['name', 'email', 'phone_no', 'cfms_ref']
    ordering = ['-created_at']
    inlines = [UserRoleInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone_no', 'profile_picture', 'id_picture')}),
        ('Organization', {'fields': ('dept', 'location', 'cfms_ref')}),
        ('Status', {'fields': ('active', 'verified_status')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'dept', 'active'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role']
    list_filter = ['role']
    search_fields = ['user__name', 'user__email', 'role__name']
