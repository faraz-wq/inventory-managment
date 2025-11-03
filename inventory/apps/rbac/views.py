"""
RBAC Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Role, Permission, RolePermission
from .serializers import (
    RoleSerializer,
    PermissionSerializer,
    AssignPermissionSerializer,
)
from .permissions import has_permission

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name']
    ordering = ['name']

    def get_permissions(self):
        # Open for Authenticated users: list, retrieve, and list_permissions
        if self.action in ['list', 'retrieve', 'list_permissions']:
            return [IsAuthenticated()]
        # Only superusers can create/update/delete or change permissions
        return [IsAdminUser()]

    @swagger_auto_schema(operation_summary='List roles', tags=['RBAC – Roles'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Create a role', tags=['RBAC – Roles'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Retrieve a role (includes permissions)', tags=['RBAC – Roles'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Update a role', tags=['RBAC – Roles'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Partial update of a role', tags=['RBAC – Roles'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Delete a role', tags=['RBAC – Roles'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Assign a permission to a role', tags=['RBAC – Role Permissions'])
    @action(detail=True, methods=['post'], url_path='assign-permission')
    def assign_permission(self, request, pk=None):
        role = self.get_object()
        serializer = AssignPermissionSerializer(data=request.data, context={'role': role})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Permission assigned successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary='Remove a permission from a role', tags=['RBAC – Role Permissions'])
    @action(detail=True, methods=['delete'], url_path=r'remove-permission/(?P<permission_id>\d+)')
    def remove_permission(self, request, pk=None, permission_id=None):
        role = self.get_object()
        try:
            role_permission = RolePermission.objects.get(role=role, permission_id=permission_id)
            role_permission.delete()
            return Response({'message': 'Permission removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        except RolePermission.DoesNotExist:
            return Response({'error': 'Permission not found for this role'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(operation_summary='List all permissions assigned to a role', tags=['RBAC – Role Permissions'])
    @action(detail=True, methods=['get'], url_path='permissions')
    def list_permissions(self, request, pk=None):
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

    @swagger_auto_schema(
        operation_summary='List permissions',
        tags=['RBAC – Permissions'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a permission',
        request_body=PermissionSerializer,
        responses={201: PermissionSerializer},
        tags=['RBAC – Permissions'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a permission',
        responses={200: PermissionSerializer},
        tags=['RBAC – Permissions'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a permission',
        request_body=PermissionSerializer,
        responses={200: PermissionSerializer},
        tags=['RBAC – Permissions'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a permission',
        request_body=PermissionSerializer,
        responses={200: PermissionSerializer},
        tags=['RBAC – Permissions'],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a permission',
        tags=['RBAC – Permissions'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)