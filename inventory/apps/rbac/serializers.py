"""
RBAC Serializers
"""
from rest_framework import serializers
from .models import Role, Permission, RolePermission


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'description']


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for RolePermission with nested permission details
    """
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        source='permission',
        write_only=True
    )

    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'permission', 'permission_id']


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model with permissions
    """
    permissions = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_count']

    def get_permissions(self, obj):
        """Get all permissions for this role"""
        role_permissions = RolePermission.objects.filter(role=obj).select_related('permission')
        return PermissionSerializer([rp.permission for rp in role_permissions], many=True).data

    def get_permission_count(self, obj):
        """Count of permissions assigned to this role"""
        return RolePermission.objects.filter(role=obj).count()


class AssignPermissionSerializer(serializers.Serializer):
    """
    Serializer for assigning permissions to a role
    """
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all()
    )

    def create(self, validated_data):
        role = self.context.get('role')
        permission = validated_data['permission_id']
        role_permission, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission
        )
        return role_permission
