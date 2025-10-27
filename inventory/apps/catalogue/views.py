"""
Catalogue Views - UPDATED
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters

from .models import ItemInfo, ItemAttribute
from .serializers import (
    ItemInfoSerializer, 
    ItemAttributeSerializer,  # You'll need to create this
    ItemInfoDetailSerializer  # Optional: for detailed view with attributes
)
from apps.rbac.permissions import has_permission


class ItemAttributeFilter(django_filters.FilterSet):
    item_id = django_filters.NumberFilter(field_name='item__id')
    item_category = django_filters.CharFilter(field_name='item__category')
    
    class Meta:
        model = ItemAttribute
        fields = ['datatype']

class ItemAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Item Attribute Definitions
    """
    queryset = ItemAttribute.objects.select_related('item').all()
    serializer_class = ItemAttributeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemAttributeFilter  # Use custom filterset instead of filterset_fields
    search_fields = ['key', 'item__item_name']
    ordering_fields = ['id', 'key', 'item__item_name']
    ordering = ['item', 'key']

    @has_permission("view_catalogue")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("create_catalogue")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("view_catalogue")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("update_catalogue")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("update_catalogue")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @has_permission("delete_catalogue")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ItemInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Item Catalogue (ItemInfo) with attribute support
    """
    queryset = ItemInfo.objects.prefetch_related('attributes').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'category', 'resource_type', 'perishability', 'item_code']
    search_fields = ['item_name', 'item_code', 'category', 'tags', 'activity_name']
    ordering_fields = ['id', 'item_name', 'item_code']
    ordering = ['item_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemInfoDetailSerializer  # Include attributes in detail view
        return ItemInfoSerializer

    @has_permission("view_catalogue")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("create_catalogue")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("view_catalogue")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("update_catalogue")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("update_catalogue")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @has_permission("delete_catalogue")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='attributes')
    def list_attributes(self, request, pk=None):
        """
        List all attribute definitions for an item type
        GET /api/catalogue/iteminfo/{id}/attributes/
        """
        item_info = self.get_object()
        attributes = item_info.attributes.all()
        serializer = ItemAttributeSerializer(attributes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='attributes')
    @has_permission("update_catalogue")
    def add_attribute(self, request, pk=None):
        """
        Add an attribute definition to an item type
        POST /api/catalogue/iteminfo/{id}/attributes/
        Body: {"key": "ram", "datatype": "string"}
        """
        item_info = self.get_object()
        serializer = ItemAttributeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(item=item_info)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='attributes/(?P<attr_id>[^/.]+)')
    @has_permission("update_catalogue")
    def update_attribute(self, request, pk=None, attr_id=None):
        """
        Update an attribute definition
        PATCH /api/catalogue/iteminfo/{id}/attributes/{attr_id}/
        Body: {"key": "memory", "datatype": "string"}
        """
        item_info = self.get_object()
        try:
            attribute = ItemAttribute.objects.get(id=attr_id, item=item_info)
            serializer = ItemAttributeSerializer(
                attribute,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ItemAttribute.DoesNotExist:
            return Response(
                {'error': 'Attribute definition not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'], url_path='attributes/(?P<attr_id>[^/.]+)')
    @has_permission("delete_catalogue")
    def delete_attribute(self, request, pk=None, attr_id=None):
        """
        Delete an attribute definition
        DELETE /api/catalogue/iteminfo/{id}/attributes/{attr_id}/
        """
        item_info = self.get_object()
        try:
            attribute = ItemAttribute.objects.get(id=attr_id, item=item_info)
            attribute.delete()
            return Response(
                {'message': 'Attribute definition deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except ItemAttribute.DoesNotExist:
            return Response(
                {'error': 'Attribute definition not found'},
                status=status.HTTP_404_NOT_FOUND
            )