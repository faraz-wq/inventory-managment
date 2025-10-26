"""
RBAC Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Role, Permission, RolePermission
from .serializers import (
    RoleSerializer,
    PermissionSerializer,
    AssignPermissionSerializer
)


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Roles
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name']
    ordering = ['name']

    @action(detail=True, methods=['post'], url_path='assign-permission')
    def assign_permission(self, request, pk=None):
        """
        Assign a permission to this role
        POST /api/rbac/roles/{id}/assign-permission/
        Body: {"permission_id": 1}
        """
        role = self.get_object()
        serializer = AssignPermissionSerializer(
            data=request.data,
            context={'role': role}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Permission assigned successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-permission/(?P<permission_id>[^/.]+)')
    def remove_permission(self, request, pk=None, permission_id=None):
        """
        Remove a permission from this role
        DELETE /api/rbac/roles/{id}/remove-permission/{permission_id}/
        """
        role = self.get_object()
        try:
            role_permission = RolePermission.objects.get(
                role=role,
                permission_id=permission_id
            )
            role_permission.delete()
            return Response(
                {'message': 'Permission removed successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except RolePermission.DoesNotExist:
            return Response(
                {'error': 'Permission not found for this role'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], url_path='permissions')
    def list_permissions(self, request, pk=None):
        """
        List all permissions for this role
        GET /api/rbac/roles/{id}/permissions/
        """
        role = self.get_object()
        role_permissions = RolePermission.objects.filter(role=role).select_related('permission')
        permissions = [rp.permission for rp in role_permissions]
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Permissions
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name']
    ordering = ['name']
