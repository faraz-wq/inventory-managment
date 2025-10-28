"""
Log Views
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_yasg.utils import swagger_auto_schema

from .models import Log
from .serializers import LogSerializer


class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Activity Logs
    Read-only: Logs are created automatically via signals
    """
    queryset = Log.objects.select_related('user').all()
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'subject_type', 'action', 'status']
    search_fields = ['subject_type', 'action', 'user__name', 'user__email']
    ordering_fields = ['id', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Non-admin users can only see their own logs.
        Admins can see all logs.
        """
        # Prevents AnonymousUser error during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Log.objects.none()

        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Log.objects.select_related('user').all()
        return Log.objects.filter(user=user).select_related('user')

    @swagger_auto_schema(
        operation_summary='List activity logs',
        operation_description=(
            "- Admins: see **all** logs\n"
            "- Regular users: see **only their own** logs"
        ),
        responses={200: LogSerializer(many=True)},
        tags=['Logs'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a single log entry',
        responses={200: LogSerializer},
        tags=['Logs'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)