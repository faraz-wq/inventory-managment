"""
BorrowRecord Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_yasg.utils import swagger_auto_schema

from .models import BorrowRecord
from .serializers import (
    BorrowRecordSerializer,
    BorrowRecordCreateSerializer,
    BorrowRecordReturnSerializer,
)
from apps.rbac.permissions import has_permission


class BorrowRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing borrow records
    """
    queryset = BorrowRecord.objects.select_related(
        'item', 'item__iteminfo', 'department', 'location',
        'issued_by', 'received_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'department', 'location', 'item',
        'issued_by', 'received_by', 'borrow_date'
    ]
    search_fields = [
        'borrower_name', 'aadhar_card', 'phone_number',
        'item__iteminfo__item_name', 'department__org_name'
    ]
    ordering_fields = ['id', 'borrow_date', 'expected_return_date', 'actual_return_date', 'created_at']
    ordering = ['-borrow_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return BorrowRecordCreateSerializer
        elif self.action == 'return_item':
            return BorrowRecordReturnSerializer
        return BorrowRecordSerializer

    # ------------------------------------------------------------------
    # Standard CRUD
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='List all borrow records',
        tags=['Borrow Records'],
    )
    @has_permission("view_borrow_records")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new borrow record (issue item to borrower)',
        request_body=BorrowRecordCreateSerializer,
        responses={201: BorrowRecordSerializer},
        tags=['Borrow Records'],
    )
    @has_permission("create_borrow_records")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        borrow_record = serializer.save()

        # Return the detailed serializer
        return Response(
            BorrowRecordSerializer(borrow_record).data,
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_summary='Retrieve a specific borrow record',
        responses={200: BorrowRecordSerializer},
        tags=['Borrow Records'],
    )
    @has_permission("view_borrow_records")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Full update of a borrow record',
        request_body=BorrowRecordSerializer,
        responses={200: BorrowRecordSerializer},
        tags=['Borrow Records'],
    )
    @has_permission("update_borrow_records")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a borrow record',
        request_body=BorrowRecordSerializer,
        responses={200: BorrowRecordSerializer},
        tags=['Borrow Records'],
    )
    @has_permission("update_borrow_records")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a borrow record',
        tags=['Borrow Records'],
    )
    @has_permission("delete_borrow_records")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Custom Actions
    # ------------------------------------------------------------------
    @swagger_auto_schema(
        operation_summary='Mark item as returned',
        request_body=BorrowRecordReturnSerializer,
        responses={200: BorrowRecordSerializer},
        tags=['Borrow Records – Return'],
    )
    @action(detail=True, methods=['post'], url_path='return')
    @has_permission("update_borrow_records")
    def return_item(self, request, pk=None):
        """
        Mark a borrowed item as returned
        """
        borrow_record = self.get_object()
        serializer = BorrowRecordReturnSerializer(
            data=request.data,
            context={'borrow_record': borrow_record, 'request': request}
        )

        if serializer.is_valid():
            returned_record = serializer.save()
            return Response(BorrowRecordSerializer(returned_record).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Get borrowing history for a specific item',
        responses={200: BorrowRecordSerializer(many=True)},
        tags=['Borrow Records – History'],
    )
    @action(detail=False, methods=['get'], url_path='item/(?P<item_id>[^/.]+)')
    @has_permission("view_borrow_records")
    def item_history(self, request, item_id=None):
        """
        Get all borrow records for a specific item
        """
        records = self.queryset.filter(item_id=item_id)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = BorrowRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Get all borrow records for a specific borrower (by Aadhar)',
        responses={200: BorrowRecordSerializer(many=True)},
        tags=['Borrow Records – History'],
    )
    @action(detail=False, methods=['get'], url_path='borrower/(?P<aadhar>[^/.]+)')
    @has_permission("view_borrow_records")
    def borrower_history(self, request, aadhar=None):
        """
        Get all borrow records for a specific borrower by Aadhar card number
        """
        records = self.queryset.filter(aadhar_card=aadhar)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = BorrowRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)
