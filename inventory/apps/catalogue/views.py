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

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ItemInfo, ItemAttribute
from .serializers import (
    ItemInfoSerializer,
    ItemAttributeSerializer,
    ItemInfoDetailSerializer,
)
from apps.rbac.permissions import has_permission


# ----------------------------------------------------------------------
# FILTERS
# ----------------------------------------------------------------------
class ItemAttributeFilter(django_filters.FilterSet):
    item_info_id = django_filters.NumberFilter(field_name='item_info__id')
    item_info_category = django_filters.CharFilter(
        field_name='item_info__category', lookup_expr='iexact'
    )

    class Meta:
        model = ItemAttribute
        fields = ['datatype', 'item_info_id', 'item_info_category']


# ----------------------------------------------------------------------
# ItemAttribute – dedicated ViewSet
# ----------------------------------------------------------------------
class ItemAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = ItemAttributeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemAttributeFilter
    queryset = ItemAttribute.objects.select_related('item_info').all()

    @swagger_auto_schema(
        operation_summary='List all attribute definitions',
        tags=['Catalogue – Attribute Definitions'],
    )
    @has_permission("view_catalogue")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new attribute definition',
        request_body=ItemAttributeSerializer,
        responses={201: ItemAttributeSerializer},
        tags=['Catalogue – Attribute Definitions'],
    )
    @has_permission("create_catalogue")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update an attribute definition',
        request_body=ItemAttributeSerializer,
        responses={200: ItemAttributeSerializer},
        tags=['Catalogue – Attribute Definitions'],
    )
    @has_permission("update_catalogue")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete an attribute definition',
        tags=['Catalogue – Attribute Definitions'],
    )
    @has_permission("delete_catalogue")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ----------------------------------------------------------------------
# ItemInfo – main catalogue ViewSet
# ----------------------------------------------------------------------
class ItemInfoViewSet(viewsets.ModelViewSet):
    queryset = ItemInfo.objects.prefetch_related('attributes').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'category', 'resource_type', 'perishability', 'item_code']
    search_fields = ['item_name', 'item_code', 'category', 'tags', 'activity_name']
    ordering_fields = ['id', 'item_name', 'item_code']
    ordering = ['item_name']

    def get_serializer_class(self):
        return ItemInfoDetailSerializer if self.action == 'retrieve' else ItemInfoSerializer

    # ----- standard actions ------------------------------------------------
    @swagger_auto_schema(
        operation_summary='List catalogue entries',
        tags=['Catalogue – ItemInfo'],
    )
    @has_permission("view_catalogue")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new catalogue entry',
        request_body=ItemInfoSerializer,
        responses={201: ItemInfoSerializer},
        tags=['Catalogue – ItemInfo'],
    )
    @has_permission("create_catalogue")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a catalogue entry (includes attributes)',
        responses={200: ItemInfoDetailSerializer},
        tags=['Catalogue – ItemInfo'],
    )
    @has_permission("view_catalogue")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Full update of a catalogue entry',
        request_body=ItemInfoSerializer,
        responses={200: ItemInfoSerializer},
        tags=['Catalogue – ItemInfo'],
    )
    @has_permission("update_catalogue")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a catalogue entry',
        request_body=ItemInfoSerializer,
        responses={200: ItemInfoSerializer},
        tags=['Catalogue – ItemInfo'],
    )
    @has_permission("update_catalogue")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a catalogue entry',
        tags=['Catalogue – ItemInfo'],
    )
    @has_permission("delete_catalogue")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # ----- custom attribute actions ----------------------------------------
    @swagger_auto_schema(
        method='get',
        operation_summary='List all attributes for this catalogue item',
        responses={200: ItemAttributeSerializer(many=True)},
        tags=['Catalogue – ItemInfo Attributes'],
    )
    @swagger_auto_schema(
        method='post',
        operation_summary='Create a new attribute definition',
        request_body=ItemAttributeSerializer,
        responses={201: ItemAttributeSerializer},
        tags=['Catalogue – ItemInfo Attributes'],
    )
    @action(detail=True, methods=['get', 'post'], url_path='attributes')
    @has_permission("update_catalogue")
    def attributes(self, request, pk=None):
        item_info = self.get_object()

        if request.method == 'GET':
            attrs = item_info.attributes.all()
            ser = ItemAttributeSerializer(attrs, many=True)
            return Response(ser.data)

        # POST
        ser = ItemAttributeSerializer(data=request.data)
        if ser.is_valid():
            ser.save(item_info=item_info)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
        item_info = self.get_object()

        try:
            attr = ItemAttribute.objects.get(id=attr_id, item_info=item_info)
        except ItemAttribute.DoesNotExist:
            return Response(
                {'error': 'Attribute not found'}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PATCH':
            ser = ItemAttributeSerializer(attr, data=request.data, partial=True)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # DELETE
        attr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        method='patch',
        operation_summary='Update an attribute definition',
        request_body=ItemAttributeSerializer,
        responses={200: ItemAttributeSerializer},
        manual_parameters=[
            openapi.Parameter(
                'attr_id', openapi.IN_PATH,
                description='ID of the ItemAttribute',
                type=openapi.TYPE_INTEGER
            )
        ],
        tags=['Catalogue – ItemInfo Attributes'],
    )
    @swagger_auto_schema(
        method='delete',
        operation_summary='Delete an attribute definition',
        responses={204: openapi.Response('Deleted')},
        manual_parameters=[
            openapi.Parameter(
                'attr_id', openapi.IN_PATH,
                description='ID of the ItemAttribute',
                type=openapi.TYPE_INTEGER
            )
        ],
        tags=['Catalogue – ItemInfo Attributes'],
    )
    @action(
        detail=True,
        methods=['patch', 'delete'],
        url_path=r'attributes/(?P<attr_id>\d+)'
    )
    @has_permission("update_catalogue")
    def attribute_detail(self, request, pk=None, attr_id=None):
        item_info = self.get_object()

        try:
            attr = ItemAttribute.objects.get(id=attr_id, item_info=item_info)
        except ItemAttribute.DoesNotExist:
            return Response(
                {'error': 'Attribute not found'}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PATCH':
            ser = ItemAttributeSerializer(attr, data=request.data, partial=True)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # DELETE
        attr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)