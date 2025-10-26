"""
User Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model

from .models import UserRole
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    AssignRoleSerializer,
    UserRoleSerializer
)
from apps.rbac.serializers import RoleSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Users
    """
    queryset = User.objects.select_related('dept', 'location').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'verified_status', 'dept', 'location']
    search_fields = ['name', 'email', 'phone_no', 'cfms_ref']
    ordering_fields = ['staff_id', 'name', 'email', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Only admins can list all users or create users
        Users can view their own profile
        """
        if self.action in ['list', 'create', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        """
        Get current logged-in user's profile
        GET /api/users/me/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_current_user(self, request):
        """
        Update current logged-in user's profile
        PATCH /api/users/me/update/
        """
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """
        Change password for current user
        POST /api/users/me/change-password/
        Body: {"old_password": "...", "new_password": "..."}
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='roles')
    def list_roles(self, request, pk=None):
        """
        List all roles for a specific user
        GET /api/users/{id}/roles/
        """
        user = self.get_object()
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        roles = [ur.role for ur in user_roles]
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign-role', permission_classes=[IsAdminUser])
    def assign_role(self, request, pk=None):
        """
        Assign a role to a user
        POST /api/users/{id}/assign-role/
        Body: {"role_id": 1}
        """
        user = self.get_object()
        serializer = AssignRoleSerializer(
            data=request.data,
            context={'user': user}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Role assigned successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-role/(?P<role_id>[^/.]+)', permission_classes=[IsAdminUser])
    def remove_role(self, request, pk=None, role_id=None):
        """
        Remove a role from a user
        DELETE /api/users/{id}/remove-role/{role_id}/
        """
        user = self.get_object()
        try:
            user_role = UserRole.objects.get(user=user, role_id=role_id)
            user_role.delete()
            return Response(
                {'message': 'Role removed successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Role not found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
