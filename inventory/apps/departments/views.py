"""
Department Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Department, DepartmentContact
from .serializers import (
    DepartmentSerializer,
    DepartmentCreateSerializer,
    DepartmentContactSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Departments
    """
    queryset = Department.objects.prefetch_related('contacts').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'org_type', 'org_code']
    search_fields = ['org_name', 'org_shortname', 'org_code', 'contact_person_name']
    ordering_fields = ['id', 'org_name', 'org_shortname']
    ordering = ['org_name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentCreateSerializer
        return DepartmentSerializer

    # ------------------------------------------------------------------
    # Standard CRUD (auto-documented with per-method swagger)
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='List departments',
        tags=['Departments'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a department',
        request_body=DepartmentCreateSerializer,
        responses={201: DepartmentSerializer},
        tags=['Departments'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a department (includes contacts)',
        responses={200: DepartmentSerializer},
        tags=['Departments'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Full update of a department',
        request_body=DepartmentCreateSerializer,
        responses={200: DepartmentSerializer},
        tags=['Departments'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a department',
        request_body=DepartmentCreateSerializer,
        responses={200: DepartmentSerializer},
        tags=['Departments'],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a department',
        tags=['Departments'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Contacts – GET / POST (same URL → per-method swagger)
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        method='get',
        operation_summary='List all contacts of a department',
        responses={200: DepartmentContactSerializer(many=True)},
        tags=['Departments – Contacts'],
    )
    @swagger_auto_schema(
        method='post',
        operation_summary='Add a new contact to a department',
        request_body=DepartmentContactSerializer,
        responses={201: DepartmentContactSerializer},
        tags=['Departments – Contacts'],
    )
    @action(detail=True, methods=['get', 'post'], url_path='contacts')
    def list_contacts(self, request, pk=None):
        department = self.get_object()

        if request.method == 'GET':
            contacts = department.contacts.all()
            ser = DepartmentContactSerializer(contacts, many=True)
            return Response(ser.data)

        # POST
        ser = DepartmentContactSerializer(data=request.data)
        if ser.is_valid():
            ser.save(dept=department)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # Contact – DELETE (single method)
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='Delete a contact from a department',
        manual_parameters=[
            openapi.Parameter(
                'contact_id',
                openapi.IN_PATH,
                description='Primary key of the DepartmentContact',
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            204: openapi.Response('Deleted'),
            404: openapi.Response('Not found'),
        },
        tags=['Departments – Contacts'],
    )
    @action(detail=True, methods=['delete'], url_path=r'contacts/(?P<contact_id>\d+)')
    def delete_contact(self, request, pk=None, contact_id=None):
        department = self.get_object()
        try:
            contact = DepartmentContact.objects.get(id=contact_id, dept=department)
            contact.delete()
            return Response(
                {'message': 'Contact deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except DepartmentContact.DoesNotExist:
            return Response(
                {'error': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND
            )