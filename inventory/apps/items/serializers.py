"""
Item Serializers
"""
from rest_framework import serializers
from .models import Item, ItemAttributeValue   
from apps.catalogue.models import ItemAttribute 


class ItemAttributeValueSerializer(serializers.ModelSerializer):
    """
    Serializer for ItemAttributeValue model (actual attribute values)
    """
    key = serializers.CharField(source='item_attribute.key', read_only=True)
    datatype = serializers.CharField(source='item_attribute.datatype', read_only=True)
    
    class Meta:
        model = ItemAttributeValue
        fields = ['id', 'item_attribute', 'key', 'value', 'datatype']
        read_only_fields = ['id', 'key', 'datatype']

    def validate(self, data):
        """
        Validate value based on datatype
        """
        item_attribute = data.get('item_attribute')
        value = data.get('value')
        
        if item_attribute and value:
            # Basic datatype validation
            if item_attribute.datatype == 'number':
                try:
                    float(value)
                except ValueError:
                    raise serializers.ValidationError(
                        f"Value must be a number for attribute {item_attribute.key}"
                    )
            elif item_attribute.datatype == 'boolean':
                if value.lower() not in ['true', 'false', '1', '0']:
                    raise serializers.ValidationError(
                        f"Value must be boolean (true/false) for attribute {item_attribute.key}"
                    )
        
        return data


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Item model
    """
    attributes = ItemAttributeValueSerializer(many=True, read_only=True, source='attribute_values')
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
    attribute_values = ItemAttributeValueSerializer(many=True, required=False)

    class Meta:
        model = Item
        fields = [
            'photo', 'eol_date', 'operational_notes', 'geocode',
            'iteminfo', 'dept', 'user', 'latitude', 'longitude', 'attribute_values'
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
        attributes_data = validated_data.pop('attribute_values', [])
        created_by = self.context['request'].user

        # Use ModelSerializer's create() to handle fields properly
        item = super().create({**validated_data, 'created_by': created_by})

        for attr_data in attributes_data:
            ItemAttributeValue.objects.create(item=item, **attr_data)

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
        if item and item.status == 'available' and value == 'verified':
            raise serializers.ValidationError(
                "Cannot transition from 'available' back to 'verified'"
            )
        return value