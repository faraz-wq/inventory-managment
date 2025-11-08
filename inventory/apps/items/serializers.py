"""
Item Serializers
"""
from rest_framework import serializers
from .models import Item, ItemAttributeValue
from apps.catalogue.models import ItemAttribute


class ItemAttributeValueSerializer(serializers.ModelSerializer):
    key = serializers.CharField(source='item_attribute.key', read_only=True)
    datatype = serializers.CharField(source='item_attribute.datatype', read_only=True)

    class Meta:
        model = ItemAttributeValue
        fields = ['id', 'item_attribute', 'key', 'value', 'datatype']
        read_only_fields = ['id', 'key', 'datatype']
        swagger_schema_name = 'ItemAttributeValue'   # exact component name

    def validate(self, data):
        item_attribute = data.get('item_attribute')
        value = data.get('value')
        if item_attribute and value:
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
    attribute_values = ItemAttributeValueSerializer(many=True, read_only=True)
    iteminfo_name = serializers.CharField(source='iteminfo.item_name', read_only=True)
    iteminfo_category = serializers.CharField(source='iteminfo.category', read_only=True)
    iteminfo_activity_name = serializers.CharField(source='iteminfo.activity_name', read_only=True)
    dept_name = serializers.CharField(source='dept.org_name', read_only=True)
    dept_short_name = serializers.CharField(source='dept.org_shortname', read_only=True)
    geocode_name = serializers.SerializerMethodField(read_only=True)
    geocode_codes = serializers.SerializerMethodField(read_only=True)
    pincode = serializers.CharField(source='geocode.village_code_ind', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'photo', 'eol_date', 'operational_notes', 'status',
            'geocode', 'geocode_name', 'pincode', 'iteminfo', 'iteminfo_name', 'iteminfo_category','iteminfo_activity_name',
            'geocode_codes',
            'dept', 'dept_name', 'dept_short_name', 'user', 'user_name',
            'created_by', 'created_by_name', 'verified_by', 'verified_by_name',
            'latitude', 'longitude', 'created_at', 'updated_at', 'attribute_values'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'verified_by']
        swagger_schema_name = 'Item'               # exact component name

    def validate(self, data):
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise serializers.ValidationError(
                "Both latitude and longitude must be provided together for geolocation"
            )
        return data

    def get_geocode_name(self, obj):
        """Return geocode name as 'village, mandal, district' when available."""
        geocode = getattr(obj, 'geocode', None)
        if not geocode:
            return ''

        parts = []
        village = getattr(geocode, 'village_name', None)
        if village:
            parts.append(village)

        # mandal may be a relation on village
        mandal = getattr(geocode, 'mandal', None)
        mandal_name = None
        if mandal:
            mandal_name = getattr(mandal, 'mandal_name', None)
        else:
            # some models may store mandal_name directly
            mandal_name = getattr(geocode, 'mandal_name', None)
        if mandal_name:
            parts.append(mandal_name)

        district = getattr(geocode, 'district', None)
        district_name = None
        if district:
            district_name = getattr(district, 'district_name', None)
        else:
            district_name = getattr(geocode, 'district_name', None)
        if district_name:
            parts.append(district_name)

        return ', '.join(parts)

    def get_geocode_codes(self, obj):
        """Return geocode AP codes as a dictionary.
        
        Returns:
            dict: Contains district_code_ap, mandal_code_ap, and village_code_ap
        """
        geocode = getattr(obj, 'geocode', None)
        if not geocode:
            return {
                'district_code_ap': None,
                'mandal_code_ap': None,
                'village_code_ap': None
            }

        # Get district code
        district = getattr(geocode, 'district', None)
        district_code = None
        if district:
            district_code = getattr(district, 'district_code_ap', None)
        if not district_code:
            district_code = getattr(geocode, 'district_code_ap', None)

        # Get mandal code
        mandal = getattr(geocode, 'mandal', None)
        mandal_code = None
        if mandal:
            mandal_code = getattr(mandal, 'mandal_code_ap', None)
        if not mandal_code:
            mandal_code = getattr(geocode, 'mandal_code_ap', None)

        # Get village code
        village_code = getattr(geocode, 'village_code_ap', None)

        return {
            'district_code_ap': district_code,
            'mandal_code_ap': mandal_code,
            'village_code_ap': village_code
        }

class ItemCreateSerializer(serializers.ModelSerializer):
    attribute_values = ItemAttributeValueSerializer(many=True, required=False)

    class Meta:
        model = Item
        fields = [
            'photo', 'eol_date', 'operational_notes', 'geocode',
            'iteminfo', 'dept', 'user', 'latitude', 'longitude', 'attribute_values'
        ]
        swagger_schema_name = 'ItemCreate'         # distinguishes create payload

    def validate(self, data):
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
        item = super().create({**validated_data, 'created_by': created_by})

        for attr_data in attributes_data:
            item_attribute = attr_data.get('item_attribute')
            if isinstance(item_attribute, dict):
                item_attribute = ItemAttribute.objects.get(id=item_attribute.get('id'))
            ItemAttributeValue.objects.create(
                item=item, item_attribute=item_attribute, value=attr_data.get('value')
            )
        return item


class ItemVerifySerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['verified', 'available'])
    operational_notes = serializers.CharField(required=False, allow_blank=True)

    swagger_schema_name = 'ItemVerify'             # non-ModelSerializer still gets a name

    def validate_status(self, value):
        item = self.context.get('item')
        if item and item.status == 'available' and value == 'verified':
            raise serializers.ValidationError(
                "Cannot transition from 'available' back to 'verified'"
            )
        return value