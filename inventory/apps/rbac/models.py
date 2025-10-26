"""
RBAC Models: Role and Permission management
"""
from django.db import models


class Role(models.Model):
    """
    Represents a role in the system (e.g., Admin, Manager, Field Officer)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class Permission(models.Model):
    """
    Represents a permission that can be assigned to roles
    (e.g., view_items, create_items, verify_items)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'permissions'
        ordering = ['name']

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """
    Many-to-many relationship between Roles and Permissions
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='permission_roles'
    )

    class Meta:
        db_table = 'role_permissions'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"
