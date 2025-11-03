"""
User Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.rbac.permissions import has_permission

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
    queryset = User.objects.select_related('dept', 'location').all()
    permission_classes = [IsAuthenticated]  # Base: must be logged in
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

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return super().get_queryset()

    # ------------------------------------------------------------------
    # Standard CRUD - Now RBAC controlled
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='List users',
        tags=['Users'],
    )
    @has_permission('view_users')  # Replace IsAdminUser
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a user',
        request_body=UserCreateSerializer,
        responses={201: UserSerializer},
        tags=['Users'],
    )
    @has_permission('create_users')  # Granular
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a user',
        responses={200: UserSerializer},
        tags=['Users'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a user',
        request_body=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['Users'],
    )
    @has_permission('update_users')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a user',
        request_body=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['Users'],
    )
    @has_permission('update_users')
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a user',
        tags=['Users'],
    )
    @has_permission('delete_users')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Current user profile (no admin required)
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='Get current user profile',
        responses={200: UserSerializer},
        tags=['Users – Profile'],
    )
    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Update current user profile',
        request_body=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['Users – Profile'],
    )
    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_current_user(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Change password for current user',
        request_body=ChangePasswordSerializer,
        responses={200: openapi.Response('Password changed')},
        tags=['Users – Profile'],
    )
    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='List roles for a user',
        responses={200: RoleSerializer(many=True)},
        tags=['Users – Roles'],
    )
    @action(detail=True, methods=['get'], url_path='roles')
    @has_permission('view_user_roles')
    def list_roles(self, request, pk=None):
        user = self.get_object()
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        roles = [ur.role for ur in user_roles]
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Assign a role to a user',
        request_body=AssignRoleSerializer,
        responses={201: openapi.Response('Role assigned')},
        tags=['Users – Roles'],
    )
    @action(detail=True, methods=['post'], url_path='assign-role')
    @has_permission('assign_user_roles')  # Replace IsAdminUser
    def assign_role(self, request, pk=None):
        user = self.get_object()
        serializer = AssignRoleSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Role assigned successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Remove a role from a user',
        manual_parameters=[
            openapi.Parameter('role_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={204: openapi.Response('Role removed')},
        tags=['Users – Roles'],
    )
    @action(detail=True, methods=['delete'], url_path=r'remove-role/(?P<role_id>\d+)')
    @has_permission('assign_user_roles')  # Same permission for remove
    def remove_role(self, request, pk=None, role_id=None):
        user = self.get_object()
        try:
            user_role = UserRole.objects.get(user=user, role_id=role_id)
            user_role.delete()
            return Response({'message': 'Role removed successfully'}, status=status.HTTP_204_NO_CONTENT)
        except UserRole.DoesNotExist:
            return Response({'error': 'Role not found for this user'}, status=status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='Verify or reject a user',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['accept', 'reject']),
                'remarks': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['action']
        ),
        responses={200: UserSerializer},
        tags=['Users – Verification'],
    )
    @action(detail=True, methods=['post'], url_path='verify')
    @has_permission('verify_users')
    def verify(self, request, pk=None):
        user = self.get_object()
        action_value = (request.data.get('action') or '').strip().lower()
        if action_value not in ('accept', 'reject'):
            return Response({'error': 'Invalid action. Use "accept" or "reject"'}, status=400)

        user.verified_status = 'verified' if action_value == 'accept' else 'rejected'
        user.save()

        return Response({
            'message': f'User {action_value}ed successfully',
            'user': UserSerializer(user).data
        }, status=200)

class RegisterView(GenericAPIView):
    """
    Public user registration endpoint.
    Uses the existing UserCreateSerializer to create a new user.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Register a new user',
        request_body=UserCreateSerializer,
        responses={201: UserSerializer},
        tags=['Users – Authentication'],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)