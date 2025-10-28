"""
RBAC Serializers
"""
from rest_framework import serializers
from .models import Role, Permission, RolePermission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'description']
        swagger_schema_name = 'Permission'   # exact component name


class RolePermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        source='permission',
        write_only=True
    )

    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'permission', 'permission_id']
        swagger_schema_name = 'RolePermission'  # optional – for nested views


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_count']
        swagger_schema_name = 'Role'         # exact component name

    def get_permissions(self, obj):
        role_permissions = RolePermission.objects.filter(role=obj).select_related('permission')
        return PermissionSerializer([rp.permission for rp in role_permissions], many=True).data

    def get_permission_count(self, obj):
        return RolePermission.objects.filter(role=obj).count()


class AssignPermissionSerializer(serializers.Serializer):
    permission_id = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all())

    swagger_schema_name = 'AssignPermission'   # non-ModelSerializer gets a name

    def create(self, validated_data):
        role = self.context.get('role')
        permission = validated_data['permission_id']
        role_permission, created = RolePermission.objects.get_or_create(
            role=role, permission=permission
        )
        return role_permission