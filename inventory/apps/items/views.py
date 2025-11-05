"""
Item Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Item, ItemAttributeValue
from .serializers import (
    ItemSerializer,
    ItemCreateSerializer,
    ItemAttributeValueSerializer,
    ItemVerifySerializer,
)
from apps.rbac.permissions import has_permission, require_scope_access


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related(
        'iteminfo', 'dept', 'geocode', 'user', 'created_by', 'verified_by'
    ).prefetch_related('attribute_values').all()
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
        return ItemCreateSerializer if self.action == 'create' else ItemSerializer

    def get_queryset(self):
        """
        Filter queryset based on user's district for District Verifiers and Data Entry Operators,
        and by department for Department Admins
        """
        queryset = super().get_queryset()

        # Superusers see everything
        if self.request.user.is_superuser:
            return queryset

        # Get user's roles
        from apps.rbac.permissions import get_user_roles
        user_roles = get_user_roles(self.request.user)

        # Check if user is a District Verifier or Data Entry Operator
        district_restricted_roles = ['District Verifier', 'Data Entry Operator']
        if any(role in district_restricted_roles for role in user_roles):
            # Get user's district
            user_district = None
            if hasattr(self.request.user, 'location') and self.request.user.location:
                user_district = self.request.user.location.district

            # If user has a district, filter items to only those in the same district
            if user_district:
                queryset = queryset.filter(geocode__district=user_district)
            else:
                # If user has no district, they see nothing
                queryset = queryset.none()

        # Check if user is a Department Admin
        elif 'Department Admin' in user_roles:
            # Get user's department
            user_dept = self.request.user.dept if hasattr(self.request.user, 'dept') else None

            # If user has a department, filter items to only those in the same department
            if user_dept:
                queryset = queryset.filter(dept=user_dept)
            else:
                # If user has no department, they see nothing
                queryset = queryset.none()

        return queryset

    # ------------------------------------------------------------------
    # Standard CRUD
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='List items',
        tags=['Items'],
    )
    @has_permission("view_items")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new item',
        request_body=ItemCreateSerializer,
        responses={201: ItemSerializer},
        tags=['Items'],
    )
    @has_permission("create_items")
    @require_scope_access({
        'District Verifier': 'district',
        'Department Admin': 'department',
        'Super Admin': None,  # No scope restriction for Super Admin
    })
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve an item (includes attribute values)',
        responses={200: ItemSerializer},
        tags=['Items'],
    )
    @has_permission("view_items")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Full update of an item',
        request_body=ItemCreateSerializer,
        responses={200: ItemSerializer},
        tags=['Items'],
    )
    @has_permission("update_items")
    @require_scope_access({
        'District Verifier': 'district',
        'Department Admin': 'department',
        'Super Admin': None,  # No scope restriction for Super Admin
    })
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of an item',
        request_body=ItemCreateSerializer,
        responses={200: ItemSerializer},
        tags=['Items'],
    )
    @has_permission("update_items")
    @require_scope_access({
        'District Verifier': 'district',
        'Department Admin': 'department',
        'Super Admin': None,  # No scope restriction for Super Admin
    })
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete an item',
        tags=['Items'],
    )
    @has_permission("delete_items")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Verify item
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='Verify an item (set status to verified/available)',
        request_body=ItemVerifySerializer,
        responses={200: ItemSerializer},
        tags=['Items – Verification'],
    )
    @action(detail=True, methods=['patch'], url_path='verify')
    @has_permission("verify_items")
    def verify_item(self, request, pk=None):
        item = self.get_object()
        serializer = ItemVerifySerializer(data=request.data, context={'item': item})

        if serializer.is_valid():
            item.status = serializer.validated_data['status']
            if 'operational_notes' in serializer.validated_data:
                item.operational_notes = serializer.validated_data['operational_notes']
            item.verified_by = request.user
            item.save()
            return Response(ItemSerializer(item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # Attributes – GET / POST (same URL)
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        method='get',
        operation_summary='List all attribute values of an item',
        responses={200: ItemAttributeValueSerializer(many=True)},
        tags=['Items – Attributes'],
    )
    @swagger_auto_schema(
        method='post',
        operation_summary='Add a new attribute value to an item',
        request_body=ItemAttributeValueSerializer,
        responses={201: ItemAttributeValueSerializer},
        tags=['Items – Attributes'],
    )
    @action(detail=True, methods=['get', 'post'], url_path='attributes')
    @has_permission("view_items")
    def attributes(self, request, pk=None):
        item = self.get_object()

        if request.method == 'GET':
            attrs = item.attribute_values.all()
            ser = ItemAttributeValueSerializer(attrs, many=True)
            return Response(ser.data)

        # POST
        ser = ItemAttributeValueSerializer(data=request.data)
        if ser.is_valid():
            ser.save(item=item)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # Attribute value – PATCH / DELETE
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        method='patch',
        operation_summary='Update an attribute value',
        request_body=ItemAttributeValueSerializer,
        responses={200: ItemAttributeValueSerializer},
        manual_parameters=[
            openapi.Parameter(
                'attr_id', openapi.IN_PATH,
                description='Primary key of the ItemAttributeValue',
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        tags=['Items – Attributes'],
    )
    @swagger_auto_schema(
        method='delete',
        operation_summary='Delete an attribute value',
        responses={204: openapi.Response('Deleted')},
        manual_parameters=[
            openapi.Parameter(
                'attr_id', openapi.IN_PATH,
                description='Primary key of the ItemAttributeValue',
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        tags=['Items – Attributes'],
    )
    @action(
        detail=True,
        methods=['patch', 'delete'],
        url_path=r'attributes/(?P<attr_id>\d+)'
    )
    @has_permission("update_items")
    def attribute_value_detail(self, request, pk=None, attr_id=None):
        item = self.get_object()

        try:
            attr_value = ItemAttributeValue.objects.get(id=attr_id, item=item)
        except ItemAttributeValue.DoesNotExist:
            return Response(
                {'error': 'Attribute value not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PATCH':
            ser = ItemAttributeValueSerializer(attr_value, data=request.data, partial=True)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # DELETE
        attr_value.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)