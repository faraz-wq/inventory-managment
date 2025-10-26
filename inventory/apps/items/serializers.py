"""
Item Serializers
"""
from rest_framework import serializers
from .models import Item, ItemAttribute


class ItemAttributeSerializer(serializers.ModelSerializer):
    """
    Serializer for ItemAttribute model
    """
    class Meta:
        model = ItemAttribute
        fields = ['id', 'key', 'value', 'datatype']


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Item model
    """
    attributes = ItemAttributeSerializer(many=True, read_only=True)
    iteminfo_name = serializers.CharField(source='iteminfo.item_name', read_only=True)
    dept_name = serializers.CharField(source='dept.org_shortname', read_only=True)
    geocode_name = serializers.CharField(source='geocode.village_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'photo', 'eol_date', 'operational_notes', 'status',
            'geocode', 'geocode_name', 'iteminfo', 'iteminfo_name',
            'dept', 'dept_name', 'user', 'user_name',
            'created_by', 'created_by_name', 'verified_by', 'verified_by_name',
            'latitude', 'longitude', 'created_at', 'updated_at', 'attributes'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'verified_by']

    def validate(self, data):
        """
        Validate that both latitude and longitude are provided together
        """
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise serializers.ValidationError(
                "Both latitude and longitude must be provided together for geolocation"
            )

        return data


class ItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating items
    """
    attributes = ItemAttributeSerializer(many=True, required=False)

    class Meta:
        model = Item
        fields = [
            'photo', 'eol_date', 'operational_notes', 'geocode',
            'iteminfo', 'dept', 'user', 'latitude', 'longitude', 'attributes'
        ]

    def validate(self, data):
        """
        Validate that both latitude and longitude are provided together
        """
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise serializers.ValidationError(
                "Both latitude and longitude must be provided together for geolocation"
            )

        return data

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        created_by = self.context['request'].user

        # Create the item
        item = Item.objects.create(created_by=created_by, **validated_data)

        # Create attributes
        for attr_data in attributes_data:
            ItemAttribute.objects.create(item=item, **attr_data)

        return item


class ItemVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying items
    """
    status = serializers.ChoiceField(choices=['verified', 'available'])
    operational_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        """
        Validate status transitions
        """
        item = self.context.get('item')
        if item.status == 'available' and value == 'verified':
            raise serializers.ValidationError(
                "Cannot transition from 'available' back to 'verified'"
            )
        return value
