"""
Catalogue Serializers
"""
from rest_framework import serializers
from .models import ItemInfo


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
