"""
Catalogue Serializers
"""
from rest_framework import serializers
from .models import ItemInfo, ItemAttribute


class ItemInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for ItemInfo (catalogue) model
    """
    tag_list = serializers.ReadOnlyField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = ItemInfo
        fields = [
            'id', 'item_code', 'item_name', 'unit', 'perishability',
            'category', 'resource_type', 'activity_name', 'tags',
            'tag_list', 'active', 'item_count'
        ]

    def get_item_count(self, obj):
        """Count of actual items using this catalogue entry"""
        return obj.items.count()

class ItemAttributeSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item_info.item_name', read_only=True)
    
    class Meta:
        model = ItemAttribute
        fields = ['id', 'item_info', 'item_name', 'key', 'datatype']
        read_only_fields = ['id']

class ItemInfoDetailSerializer(ItemInfoSerializer):
    # Include attributes in detail view
    attributes = ItemAttributeSerializer(many=True, read_only=True)
    
    class Meta(ItemInfoSerializer.Meta):
        fields = ItemInfoSerializer.Meta.fields + ['attributes']