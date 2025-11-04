"""
BorrowRecord Serializers
"""
from rest_framework import serializers
from .models import BorrowRecord
from apps.items.models import Item


class BorrowRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for reading borrow records with related information
    """
    item_name = serializers.CharField(source='item.iteminfo.item_name', read_only=True)
    department_name = serializers.CharField(source='department.org_shortname', read_only=True)
    location_name = serializers.CharField(source='location.village_name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.name', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'item', 'item_name', 'borrower_name', 'aadhar_card',
            'phone_number', 'address', 'department', 'department_name',
            'location', 'location_name', 'borrow_date', 'expected_return_date',
            'actual_return_date', 'status', 'borrow_notes', 'return_notes',
            'issued_by', 'issued_by_name', 'received_by', 'received_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'borrow_date', 'issued_by', 'received_by']
        swagger_schema_name = 'BorrowRecord'


class BorrowRecordCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new borrow records
    """
    class Meta:
        model = BorrowRecord
        fields = [
            'item', 'borrower_name', 'aadhar_card', 'phone_number',
            'address', 'department', 'location', 'expected_return_date',
            'borrow_notes'
        ]
        swagger_schema_name = 'BorrowRecordCreate'

    def validate_item(self, value):
        """
        Validate that the item exists and is available for borrowing
        """
        if not value:
            raise serializers.ValidationError("Item is required")

        # Check if item is already borrowed
        if value.status == 'borrowed':
            raise serializers.ValidationError(
                f"This item is already borrowed. Current status: {value.status}"
            )

        # Only allow borrowing of available or verified items
        if value.status not in ['available', 'verified']:
            raise serializers.ValidationError(
                f"Item must be 'available' or 'verified' to be borrowed. Current status: {value.status}"
            )

        return value

    def validate_aadhar_card(self, value):
        """
        Validate Aadhar card number format
        """
        if not value.isdigit():
            raise serializers.ValidationError("Aadhar card must contain only digits")

        if len(value) != 12:
            raise serializers.ValidationError("Aadhar card must be exactly 12 digits")

        return value

    def validate_phone_number(self, value):
        """
        Validate phone number format
        """
        # Remove any spaces, dashes, and plus signs
        cleaned = value.replace(' ', '').replace('-', '').replace('+', '')

        if not cleaned.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")

        if len(cleaned) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")

        return value

    def create(self, validated_data):
        """
        Create borrow record and automatically set issued_by to current user
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['issued_by'] = request.user

        # Status is automatically set to 'borrowed' by model default
        borrow_record = super().create(validated_data)
        return borrow_record


class BorrowRecordReturnSerializer(serializers.Serializer):
    """
    Serializer for marking items as returned
    """
    return_notes = serializers.CharField(required=False, allow_blank=True)
    actual_return_date = serializers.DateTimeField(required=False)

    swagger_schema_name = 'BorrowRecordReturn'

    def validate(self, data):
        """
        Validate that the borrow record can be returned
        """
        borrow_record = self.context.get('borrow_record')

        if not borrow_record:
            raise serializers.ValidationError("Borrow record not found")

        if borrow_record.status == 'returned':
            raise serializers.ValidationError("This item has already been returned")

        return data

    def save(self):
        """
        Update the borrow record to mark it as returned
        """
        from django.utils import timezone

        borrow_record = self.context.get('borrow_record')
        request = self.context.get('request')

        borrow_record.status = 'returned'
        borrow_record.return_notes = self.validated_data.get('return_notes', '')
        borrow_record.actual_return_date = self.validated_data.get('actual_return_date', timezone.now())

        if request and hasattr(request, 'user'):
            borrow_record.received_by = request.user

        borrow_record.save()
        return borrow_record
