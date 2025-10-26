"""
Script to create initial RBAC permissions and roles
Run this after migrations: python manage.py shell < setup_initial_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.rbac.models import Permission, Role, RolePermission

# Create Permissions
permissions_data = [
    ('view_items', 'Can view items'),
    ('create_items', 'Can create items'),
    ('update_items', 'Can update items'),
    ('delete_items', 'Can delete items'),
    ('verify_items', 'Can verify items'),
    ('view_users', 'Can view users'),
    ('create_users', 'Can create users'),
    ('update_users', 'Can update users'),
    ('delete_users', 'Can delete users'),
    ('view_departments', 'Can view departments'),
    ('create_departments', 'Can create departments'),
    ('update_departments', 'Can update departments'),
    ('delete_departments', 'Can delete departments'),
    ('view_logs', 'Can view activity logs'),
    ('manage_roles', 'Can manage roles and permissions'),
]

print("Creating permissions...")
for name, description in permissions_data:
    permission, created = Permission.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    if created:
        print(f"  ✓ Created: {name}")
    else:
        print(f"  - Already exists: {name}")

# Create Roles
roles_data = [
    ('Admin', 'System administrator with full access'),
    ('Manager', 'Department manager with item and user management'),
    ('Field Officer', 'Field officer with item creation and verification'),
    ('Viewer', 'Read-only access to items and reports'),
]

print("\nCreating roles...")
for name, description in roles_data:
    role, created = Role.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    if created:
        print(f"  ✓ Created: {name}")
    else:
        print(f"  - Already exists: {name}")

# Assign Permissions to Roles
print("\nAssigning permissions to roles...")

# Admin - All permissions
admin_role = Role.objects.get(name='Admin')
all_permissions = Permission.objects.all()
for perm in all_permissions:
    RolePermission.objects.get_or_create(role=admin_role, permission=perm)
print(f"  ✓ Admin: {all_permissions.count()} permissions")

# Manager - Most permissions except delete
manager_role = Role.objects.get(name='Manager')
manager_perms = [
    'view_items', 'create_items', 'update_items', 'verify_items',
    'view_users', 'create_users', 'update_users',
    'view_departments', 'view_logs'
]
for perm_name in manager_perms:
    perm = Permission.objects.get(name=perm_name)
    RolePermission.objects.get_or_create(role=manager_role, permission=perm)
print(f"  ✓ Manager: {len(manager_perms)} permissions")

# Field Officer - Item management only
field_role = Role.objects.get(name='Field Officer')
field_perms = [
    'view_items', 'create_items', 'update_items', 'verify_items'
]
for perm_name in field_perms:
    perm = Permission.objects.get(name=perm_name)
    RolePermission.objects.get_or_create(role=field_role, permission=perm)
print(f"  ✓ Field Officer: {len(field_perms)} permissions")

# Viewer - Read-only access
viewer_role = Role.objects.get(name='Viewer')
viewer_perms = ['view_items', 'view_departments', 'view_logs']
for perm_name in viewer_perms:
    perm = Permission.objects.get(name=perm_name)
    RolePermission.objects.get_or_create(role=viewer_role, permission=perm)
print(f"  ✓ Viewer: {len(viewer_perms)} permissions")

print("\n" + "="*50)
print("Initial data setup complete!")
print("="*50)
print("\nSummary:")
print(f"  Permissions: {Permission.objects.count()}")
print(f"  Roles: {Role.objects.count()}")
print(f"  Role-Permission mappings: {RolePermission.objects.count()}")
