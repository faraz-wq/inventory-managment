# Role-Based Scope Access Decorator Guide

## Overview

The `require_scope_access` decorator provides role-based access control with district and department scope restrictions. This ensures that users can only create and update items/users belonging to their assigned district or department.

## Features

- **District Verifier**: Can only create/update items and users in their district
- **Department Admin**: Can only create/update items and users in their department
- **Super Admin**: Has unrestricted access to all districts and departments
- **Superuser Bypass**: Django superusers automatically bypass all scope checks
- **Reusable**: Can be applied to any ViewSet method
- **Flexible**: Supports multiple roles with different scope restrictions

## Location

The decorator is defined in: `inventory/apps/rbac/permissions.py`

## Basic Usage

### Import the Decorator

```python
from apps.rbac.permissions import has_permission, require_scope_access
```

### Apply to ViewSet Methods

```python
from rest_framework import viewsets
from apps.rbac.permissions import has_permission, require_scope_access

class ItemViewSet(viewsets.ModelViewSet):
    # ... queryset and other configurations ...

    @has_permission("create_items")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
        'super_admin': None,  # No scope restriction
    })
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("update_items")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
        'super_admin': None,
    })
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
```

## Decorator Parameters

The `require_scope_access` decorator accepts a dictionary that maps role names to their scope restrictions:

```python
{
    'role_name': 'scope_type',
    # ...
}
```

### Scope Types

- `'district'` - User can only access items/users in their district
- `'department'` - User can only access items/users in their department
- `None` - No scope restriction (full access)

### Role Names

Role names must match the `name` field in your `Role` model. Common examples:
- `'district_verifier'`
- `'department_admin'`
- `'super_admin'`
- `'field_officer'`
- etc.

## How It Works

### For Create Operations

When creating new items or users, the decorator:

1. Checks if the user has one of the allowed roles
2. For `district` scope:
   - Validates that the `geocode` (for items) or `location` (for users) field in the request belongs to the user's district
   - Blocks the request if the location is outside their district
3. For `department` scope:
   - Validates that the `dept` field in the request matches the user's department
   - Blocks the request if the department doesn't match

### For Update Operations

When updating existing items or users, the decorator:

1. Checks if the user has one of the allowed roles
2. Fetches the target object using `self.get_object()`
3. For `district` scope:
   - Compares the user's district with the object's district
   - Blocks the request if districts don't match
4. For `department` scope:
   - Compares the user's department with the object's department
   - Blocks the request if departments don't match

## Examples

### Example 1: Items ViewSet

```python
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated]

    @has_permission("create_items")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
        'super_admin': None,
    })
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("update_items")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
        'super_admin': None,
    })
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
```

### Example 2: Users ViewSet

```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @has_permission("create_users")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
        'hr_admin': None,  # HR can create users anywhere
    })
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("update_users")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
        'hr_admin': None,
    })
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
```

### Example 3: Custom Action

```python
class ItemViewSet(viewsets.ModelViewSet):
    # ...

    @action(detail=True, methods=['patch'], url_path='verify')
    @has_permission("verify_items")
    @require_scope_access({
        'district_verifier': 'district',
        'department_admin': 'department',
    })
    def verify_item(self, request, pk=None):
        item = self.get_object()
        # Custom verification logic
        item.verified_by = request.user
        item.status = 'verified'
        item.save()
        return Response({'status': 'Item verified'})
```

## Response Messages

The decorator returns clear error messages when access is denied:

### Authentication Required
```json
{
    "error": "Authentication required"
}
```
Status: 401 UNAUTHORIZED

### Role Not Allowed
```json
{
    "error": "Access denied. Required roles: district_verifier, department_admin"
}
```
Status: 403 FORBIDDEN

### District Scope Violation (Create)
```json
{
    "error": "Access denied. You can only create items in your district."
}
```
Status: 403 FORBIDDEN

### District Scope Violation (Update)
```json
{
    "error": "Access denied. You can only modify items/users in your district."
}
```
Status: 403 FORBIDDEN

### Department Scope Violation
```json
{
    "error": "Access denied. You can only create items/users in your department."
}
```
Status: 403 FORBIDDEN

## Requirements

### User Model Requirements

Users must have:
- `dept` field (ForeignKey to Department)
- `location` field (ForeignKey to Village)

### Item Model Requirements

Items must have:
- `dept` field (ForeignKey to Department)
- `geocode` field (ForeignKey to Village) - for district scope checking

### Location Model Requirements

Villages must have:
- `district` field (ForeignKey to District)

## Helper Functions

The decorator uses these helper functions (available for your own use):

### `get_user_roles(user)`
Returns a list of role names for a user.

```python
from apps.rbac.permissions import get_user_roles

roles = get_user_roles(request.user)
# Returns: ['district_verifier', 'field_officer']
```

### `check_district_scope(user, target_object)`
Checks if a user's district matches the target object's district.

```python
from apps.rbac.permissions import check_district_scope

if check_district_scope(request.user, item):
    # User can access this item
    pass
```

### `check_department_scope(user, target_object)`
Checks if a user's department matches the target object's department.

```python
from apps.rbac.permissions import check_department_scope

if check_department_scope(request.user, item):
    # User can access this item
    pass
```

## Setup Instructions

### 1. Create Required Roles

Make sure you have the required roles in your database:

```python
from apps.rbac.models import Role

Role.objects.create(name='district_verifier', description='Can verify items in their district')
Role.objects.create(name='department_admin', description='Can manage items in their department')
Role.objects.create(name='super_admin', description='Full system access')
```

### 2. Assign Roles to Users

```python
from apps.users.models import User, UserRole
from apps.rbac.models import Role

user = User.objects.get(email='john@example.com')
role = Role.objects.get(name='district_verifier')

UserRole.objects.create(user=user, role=role)
```

### 3. Set User's District and Department

```python
from apps.users.models import User
from apps.departments.models import Department
from apps.locations.models import Village

user = User.objects.get(email='john@example.com')
user.dept = Department.objects.get(org_code='DEPT001')
user.location = Village.objects.get(village_code_ap='12345')
user.save()
```

## Combining with Permission Checks

Always use `@has_permission()` decorator **before** `@require_scope_access()`:

```python
@has_permission("update_items")  # ✅ Check permission first
@require_scope_access({          # ✅ Then check scope
    'district_verifier': 'district',
})
def update(self, request, *args, **kwargs):
    return super().update(request, *args, **kwargs)
```

This ensures that:
1. User has the required permission to perform the action
2. User's scope (district/department) allows them to access the specific object

## Superuser and Super Admin

- **Django Superusers** (`is_superuser=True`): Automatically bypass all checks
- **Super Admin Role**: Include in the decorator with `None` scope for unrestricted access

```python
@require_scope_access({
    'district_verifier': 'district',
    'department_admin': 'department',
    'super_admin': None,  # ✅ Unrestricted access
})
```

## Testing

### Test District Verifier

1. Create a user with `district_verifier` role
2. Assign the user to a district (via village location)
3. Try to create an item in a different district → Should be blocked
4. Try to create an item in the same district → Should succeed

### Test Department Admin

1. Create a user with `department_admin` role
2. Assign the user to a department
3. Try to create an item in a different department → Should be blocked
4. Try to create an item in the same department → Should succeed

### Test Super Admin

1. Create a user with `super_admin` role
2. Try to create items in any district/department → Should succeed

## Best Practices

1. **Always combine with permission checks**: Use `@has_permission()` before `@require_scope_access()`
2. **Use consistent role names**: Define role names as constants to avoid typos
3. **Set clear scope types**: Use `'district'`, `'department'`, or `None` consistently
4. **Handle missing location/department**: Ensure users have their location and department set
5. **Test thoroughly**: Test with different roles and scenarios
6. **Document custom roles**: If you add new roles, document them clearly

## Troubleshooting

### "Access denied. Required roles: ..."

- **Cause**: User doesn't have any of the specified roles
- **Solution**: Assign the appropriate role to the user

### "Access denied. You can only create items in your district."

- **Cause**: User is trying to create/update an item outside their district
- **Solution**: Ensure the user is creating items in their assigned district

### "Access denied. You can only create items/users in your department."

- **Cause**: User is trying to create/update an item outside their department
- **Solution**: Ensure the user is creating items in their assigned department

### "Invalid location data: ..."

- **Cause**: The provided location/geocode ID doesn't exist
- **Solution**: Verify the location ID is valid

### User with correct role still blocked

- **Check**: User has `location` and `dept` fields set correctly
- **Check**: Role name matches exactly (case-sensitive)
- **Check**: User is not a Django superuser (they would bypass all checks)

## Migration Notes

If you're adding this to an existing application:

1. Audit existing user assignments to ensure they have proper location and department
2. Create the required roles in the database
3. Assign roles to existing users
4. Test with a non-production environment first
5. Monitor logs for access denied errors and adjust as needed
