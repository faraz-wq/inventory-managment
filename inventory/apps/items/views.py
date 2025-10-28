"""
Item Views - CORRECTED
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Item, ItemAttributeValue  # ← CORRECTED IMPORT
from .serializers import (
    ItemSerializer,
    ItemCreateSerializer,
    ItemAttributeValueSerializer,  # This should serialize ItemAttributeValue
    ItemVerifySerializer
)
from apps.rbac.permissions import has_permission


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Items
    """
    queryset = Item.objects.select_related(
        'iteminfo', 'dept', 'geocode', 'user', 'created_by', 'verified_by'
    ).prefetch_related('attribute_values').all()  # 'attributes' refers to ItemAttributeValue via related_name
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'dept', 'geocode', 'iteminfo',
        'geocode__district', 'geocode__mandal', 'created_by', 'verified_by'
    ]
    search_fields = [
        'iteminfo__item_name', 'iteminfo__item_code',
        'operational_notes', 'dept__org_name'
    ]
    ordering_fields = ['id', 'created_at', 'updated_at', 'eol_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ItemCreateSerializer
        return ItemSerializer

    @has_permission("view_items")
    def list(self, request, *args, **kwargs):
        """List items - requires view_items permission"""
        return super().list(request, *args, **kwargs)

    @has_permission("create_items")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("view_items")
    def retrieve(self, request, *args, **kwargs):
        """Retrieve item - requires view_items permission"""
        return super().retrieve(request, *args, **kwargs)

    @has_permission("update_items")
    def update(self, request, *args, **kwargs):
        """Update item - requires update_items permission"""
        return super().update(request, *args, **kwargs)

    @has_permission("update_items")
    def partial_update(self, request, *args, **kwargs):
        """Partial update item - requires update_items permission"""
        return super().partial_update(request, *args, **kwargs)

    @has_permission("delete_items")
    def destroy(self, request, *args, **kwargs):
        """Delete item - requires delete_items permission"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'], url_path='verify')
    @has_permission("verify_items")
    def verify_item(self, request, pk=None):
        """
        Verify an item
        PATCH /api/items/{id}/verify/
        Body: {"status": "verified", "operational_notes": "..."}
        """
        item = self.get_object()
        serializer = ItemVerifySerializer(
            data=request.data,
            context={'item': item}
        )

        if serializer.is_valid():
            item.status = serializer.validated_data['status']
            if 'operational_notes' in serializer.validated_data:
                item.operational_notes = serializer.validated_data['operational_notes']
            item.verified_by = request.user
            item.save()

            return Response(ItemSerializer(item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'], url_path='attributes')
    def attributes(self, request, pk=None):
        item = self.get_object()

        if request.method == 'GET':
            attrs = item.attribute_values.all()
            serializer = ItemAttributeValueSerializer(attrs, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = ItemAttributeValueSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(item=item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['patch', 'delete'],
        url_path=r'attributes/(?P<attr_id>\d+)'
    )
    @has_permission("update_items")
    def attribute_value_detail(self, request, pk=None, attr_id=None):
        """
        Handle:
        - PATCH  /api/items/<id>/attributes/<attr_id>/   → update value
        - DELETE /api/items/<id>/attributes/<attr_id>/   → delete value
        """
        item_info = self.get_object()

        try:
            attr_value = ItemAttributeValue.objects.get(id=attr_id, item=item_info)
        except ItemAttributeValue.DoesNotExist:
            return Response(
                {'error': 'Attribute value not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PATCH':
            serializer = ItemAttributeValueSerializer(
                attr_value, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # DELETE
        attr_value.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)