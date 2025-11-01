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
    ('verify_users', 'Can verify users'),
    ('view_departments', 'Can view departments'),
    ('create_departments', 'Can create departments'),
    ('update_departments', 'Can update departments'),
    ('delete_departments', 'Can delete departments'),
    ('view_logs', 'Can view activity logs'),
    ('manage_roles', 'Can manage roles and permissions'),
    ('view_catalogue', 'Can view catalogue entries and attribute definitions'),
    ('create_catalogue', 'Can create catalogue entries and attribute definitions'),
    ('update_catalogue', 'Can update catalogue entries and attribute definitions'),
    ('delete_catalogue', 'Can delete catalogue entries and attribute definitions'),

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
    # Production roles
    ('Super Admin', 'State-level super administrator with full access and masters management'),
    ('Department Admin', 'Department administrator: bulk uploads and department reports'),
    ('District Verifier', 'Verifier for a district: validate and verify items in their district'),
    ('Data Entry User', 'Creates records quickly; limited to own created records'),
    ('Read-Only', 'Search/browse only (SEOC/EOC/Ops)'),
    ('RBAC Manager', 'Manages roles and basic permissions for prototype'),
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
super_role = Role.objects.get(name='Super Admin')
all_permissions = Permission.objects.all()
for perm in all_permissions:
    RolePermission.objects.get_or_create(role=super_role, permission=perm)
print(f"  ✓ Super Admin: {all_permissions.count()} permissions")

# Helper to fetch permission if it exists; print a short warning otherwise
def _get_permission(name):
    try:
        return Permission.objects.get(name=name)
    except Permission.DoesNotExist:
        print(f"  ! Permission missing, skipping: {name}")
        return None

# Manager - Most permissions except delete
dept_admin_role = Role.objects.get(name='Department Admin')
dept_admin_perms = [
    'view_items', 'create_items', 'update_items',
    'view_users',
    'view_departments', 'bulk_upload', 'export_data', 'view_logs'
]
count = 0
for perm_name in dept_admin_perms:
    perm = _get_permission(perm_name)
    if perm:
        RolePermission.objects.get_or_create(role=dept_admin_role, permission=perm)
        count += 1
print(f"  ✓ Department Admin: {count} permissions assigned (requested {len(dept_admin_perms)})")

# Field Officer - Item management only
verifier_role = Role.objects.get(name='District Verifier')
verifier_perms = [
    'view_items', 'verify_items', 'verify_district', 'view_logs'
]
count = 0
for perm_name in verifier_perms:
    perm = _get_permission(perm_name)
    if perm:
        RolePermission.objects.get_or_create(role=verifier_role, permission=perm)
        count += 1
print(f"  ✓ District Verifier: {count} permissions assigned (requested {len(verifier_perms)})")

# Viewer - Read-only access
data_entry_role = Role.objects.get(name='Data Entry User')
data_entry_perms = ['view_items', 'create_items', 'read_only_search']
count = 0
for perm_name in data_entry_perms:
    perm = _get_permission(perm_name)
    if perm:
        RolePermission.objects.get_or_create(role=data_entry_role, permission=perm)
        count += 1
print(f"  ✓ Data Entry User: {count} permissions assigned (requested {len(data_entry_perms)})")

read_only_role = Role.objects.get(name='Read-Only')
read_only_perms = ['view_items', 'view_departments', 'view_logs', 'read_only_search', 'export_data']
count = 0
for perm_name in read_only_perms:
    perm = _get_permission(perm_name)
    if perm:
        RolePermission.objects.get_or_create(role=read_only_role, permission=perm)
        count += 1
print(f"  ✓ Read-Only: {count} permissions assigned (requested {len(read_only_perms)})")

rbac_role = Role.objects.get(name='RBAC Manager')
rbac_perms = ['manage_roles', 'rbac_manage_basic']
count = 0
for perm_name in rbac_perms:
    perm = _get_permission(perm_name)
    if perm:
        RolePermission.objects.get_or_create(role=rbac_role, permission=perm)
        count += 1
print(f"  ✓ RBAC Manager: {count} permissions assigned (requested {len(rbac_perms)})")

print("\n" + "="*50)
print("Initial data setup complete!")
print("="*50)
print("\nSummary:")
print(f"  Permissions: {Permission.objects.count()}")
print(f"  Roles: {Role.objects.count()}")
print(f"  Role-Permission mappings: {RolePermission.objects.count()}")
