"""
Custom Permission Classes and Decorators for RBAC
"""
from functools import wraps
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from .models import RolePermission


class HasPermission(permissions.BasePermission):
    """
    Custom permission class to check if user has specific permission
    """
    def __init__(self, permission_name):
        self.permission_name = permission_name

    def has_permission(self, request, view):
        # Superusers bypass all permission checks
        if request.user and request.user.is_superuser:
            return True

        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Get user's roles
        from apps.users.models import UserRole
        user_roles = UserRole.objects.filter(user=request.user).select_related('role')

        # Check if any of the user's roles have the required permission
        for user_role in user_roles:
            has_perm = RolePermission.objects.filter(
                role=user_role.role,
                permission__name=self.permission_name
            ).exists()
            if has_perm:
                return True

        return False


def has_permission(permission_name):
    """
    Decorator to check if user has specific permission
    Usage:
        @has_permission("view_items")
        def get(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Superusers bypass all permission checks
            if request.user and request.user.is_superuser:
                return func(self, request, *args, **kwargs)

            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get user's roles
            from apps.users.models import UserRole
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')

            # Check if any of the user's roles have the required permission
            for user_role in user_roles:
                has_perm = RolePermission.objects.filter(
                    role=user_role.role,
                    permission__name=permission_name
                ).exists()
                if has_perm:
                    return func(self, request, *args, **kwargs)

            return Response(
                {'error': f'Permission denied. Required permission: {permission_name}'},
                status=status.HTTP_403_FORBIDDEN
            )
        return wrapper
    return decorator


def check_user_permission(user, permission_name):
    """
    Helper function to check if a user has a specific permission
    Returns True if user has the permission, False otherwise
    """
    # Superusers have all permissions
    if user.is_superuser:
        return True

    # Get user's roles
    from apps.users.models import UserRole
    user_roles = UserRole.objects.filter(user=user).select_related('role')

    # Check if any of the user's roles have the required permission
    for user_role in user_roles:
        has_perm = RolePermission.objects.filter(
            role=user_role.role,
            permission__name=permission_name
        ).exists()
        if has_perm:
            return True

    return False
