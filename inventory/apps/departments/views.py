"""
Department Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Department, DepartmentContact
from .serializers import (
    DepartmentSerializer,
    DepartmentCreateSerializer,
    DepartmentContactSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Departments
    """
    queryset = Department.objects.all()
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

    @action(detail=True, methods=['get'], url_path='contacts')
    def list_contacts(self, request, pk=None):
        """
        List all contacts for a specific department
        GET /api/departments/{id}/contacts/
        """
        department = self.get_object()
        contacts = department.contacts.all()
        serializer = DepartmentContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='contacts')
    def add_contact(self, request, pk=None):
        """
        Add a contact to a department
        POST /api/departments/{id}/contacts/
        Body: {"contact_type": "mobile", "contact_value": "+91-1234567890"}
        """
        department = self.get_object()
        serializer = DepartmentContactSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(dept=department)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='contacts/(?P<contact_id>[^/.]+)')
    def delete_contact(self, request, pk=None, contact_id=None):
        """
        Delete a contact from a department
        DELETE /api/departments/{id}/contacts/{contact_id}/
        """
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
