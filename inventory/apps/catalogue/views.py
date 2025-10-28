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
    item_info_id = django_filters.NumberFilter(field_name='item_info__id')
    item_info_category = django_filters.CharFilter(field_name='item_info__category', lookup_expr='iexact')

    class Meta:
        model = ItemAttribute
        fields = ['datatype', 'item_info_id', 'item_info_category']

class ItemAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Item Attribute Definitions
    """
    serializer_class = ItemAttributeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemAttributeFilter  # Use custom filterset instead of filterset_fields

    @has_permission("view_catalogue")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("create_catalogue")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("update_catalogue")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

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

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path='attributes'
    )
    @has_permission("update_catalogue")  # Only applies to POST
    def attributes(self, request, pk=None):
        """
        Handle both:
        - GET  /api/catalogue/<id>/attributes/     → list attributes
        - POST /api/catalogue/<id>/attributes/     → add attribute
        """
        item_info = self.get_object()

        if request.method == 'GET':
            # List attributes
            attributes = item_info.attributes.all()
            serializer = ItemAttributeSerializer(attributes, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            # Create attribute
            serializer = ItemAttributeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(item_info=item_info)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
            detail=True,
            methods=['patch', 'delete'],
            url_path=r'attributes/(?P<attr_id>\d+)'
        )
    def attribute_detail(self, request, pk=None, attr_id=None):
        """
        PATCH  /api/catalogue/<id>/attributes/<attr_id>/   → update
        DELETE /api/catalogue/<id>/attributes/<attr_id>/   → delete
        """
        item_info = self.get_object()

        try:
            attr = ItemAttribute.objects.get(id=attr_id, item_info=item_info)
        except ItemAttribute.DoesNotExist:
            return Response(
                {'error': 'Attribute not found'}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PATCH':
            serializer = ItemAttributeSerializer(
                attr, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # DELETE
        attr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)