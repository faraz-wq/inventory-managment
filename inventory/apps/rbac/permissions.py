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


def get_user_roles(user):
    """
    Helper function to get all role names for a user
    Returns a list of role names
    """
    from apps.users.models import UserRole
    return list(
        UserRole.objects.filter(user=user)
        .select_related('role')
        .values_list('role__name', flat=True)
    )


def check_district_scope(user, target_object):
    """
    Check if user's district matches the target object's district

    Args:
        user: The user making the request
        target_object: The object being accessed (Item, User, etc.)

    Returns:
        True if districts match, False otherwise
    """
    # Get user's district through their village location
    user_district = None
    if hasattr(user, 'location') and user.location:
        user_district = user.location.district

    # Get target object's district
    target_district = None

    # Check if target is a User object
    if hasattr(target_object, 'location') and target_object.location:
        target_district = target_object.location.district

    # Check if target is an Item object (has geocode field)
    elif hasattr(target_object, 'geocode') and target_object.geocode:
        target_district = target_object.geocode.district

    # Check if target has direct district field
    elif hasattr(target_object, 'district'):
        target_district = target_object.district

    # If either user or target has no district, deny access
    if not user_district or not target_district:
        return False

    return user_district.id == target_district.id


def check_department_scope(user, target_object):
    """
    Check if user's department matches the target object's department

    Args:
        user: The user making the request
        target_object: The object being accessed (Item, User, etc.)

    Returns:
        True if departments match, False otherwise
    """
    # Get user's department
    user_dept = user.dept if hasattr(user, 'dept') else None

    # Get target object's department
    target_dept = None

    # Check if target has dept field
    if hasattr(target_object, 'dept'):
        target_dept = target_object.dept

    # If either user or target has no department, deny access
    if not user_dept or not target_dept:
        return False

    return user_dept.id == target_dept.id


def require_scope_access(allowed_roles_with_scopes):
    """
    Reusable decorator that enforces role-based district and department access control.

    Args:
        allowed_roles_with_scopes: Dict mapping role names to their scope restrictions
            Example: {
                'District Verifier': 'district',
                'Department Admin': 'department',
                'Super Admin': None  # No scope restriction
            }

    Usage:
        @require_scope_access({
            'District Verifier': 'district',
            'Department Admin': 'department',
        })
        def update(self, request, *args, **kwargs):
            # Your view logic here
            ...

    The decorator will:
    1. Check if user has one of the allowed roles
    2. For create operations: validate request data against user's scope
    3. For update operations: validate the target object against user's scope
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Superusers bypass all checks
            if request.user and request.user.is_superuser:
                return func(self, request, *args, **kwargs)

            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get user's roles
            user_roles = get_user_roles(request.user)

            # Check if user has any of the allowed roles
            matching_role = None
            required_scope = None

            for role_name, scope in allowed_roles_with_scopes.items():
                if role_name in user_roles:
                    matching_role = role_name
                    required_scope = scope
                    break

            if not matching_role:
                return Response(
                    {
                        'error': 'Access denied. Required roles: ' +
                                ', '.join(allowed_roles_with_scopes.keys())
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # If no scope restriction for this role, allow access
            if required_scope is None:
                return func(self, request, *args, **kwargs)

            # For update/delete operations, check the target object
            if kwargs.get('pk'):
                try:
                    # Get the object being accessed
                    target_object = self.get_object()

                    # Check scope based on role
                    if required_scope == 'district':
                        if not check_district_scope(request.user, target_object):
                            return Response(
                                {'error': 'Access denied. You can only modify items/users in your district.'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                    elif required_scope == 'department':
                        if not check_department_scope(request.user, target_object):
                            return Response(
                                {'error': 'Access denied. You can only modify items/users in your department.'},
                                status=status.HTTP_403_FORBIDDEN
                            )

                except Exception as e:
                    return Response(
                        {'error': f'Error checking access: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # For create operations, validate the data being submitted
            else:
                data = request.data

                # Check district scope for create
                if required_scope == 'district':
                    # For items, check geocode field
                    if 'geocode' in data:
                        try:
                            from apps.locations.models import Village
                            village = Village.objects.select_related('district').get(id=data['geocode'])
                            user_district = request.user.location.district if request.user.location else None

                            if not user_district or village.district.id != user_district.id:
                                return Response(
                                    {'error': 'Access denied. You can only create items in your district.'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                        except Exception as e:
                            return Response(
                                {'error': f'Invalid location data: {str(e)}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                    # For users, check location field
                    elif 'location' in data:
                        try:
                            from apps.locations.models import Village
                            village = Village.objects.select_related('district').get(id=data['location'])
                            user_district = request.user.location.district if request.user.location else None

                            if not user_district or village.district.id != user_district.id:
                                return Response(
                                    {'error': 'Access denied. You can only create users in your district.'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                        except Exception as e:
                            return Response(
                                {'error': f'Invalid location data: {str(e)}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                # Check department scope for create
                elif required_scope == 'department':
                    if 'dept' in data:
                        user_dept = request.user.dept

                        if not user_dept or str(data['dept']) != str(user_dept.id):
                            return Response(
                                {'error': 'Access denied. You can only create items/users in your department.'},
                                status=status.HTTP_403_FORBIDDEN
                            )

            return func(self, request, *args, **kwargs)

        return wrapper
    return decorator
