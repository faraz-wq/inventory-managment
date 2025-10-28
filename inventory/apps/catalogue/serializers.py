"""
Catalogue Serializers
"""
from rest_framework import serializers
from .models import ItemInfo, ItemAttribute


class ItemInfoSerializer(serializers.ModelSerializer):
    tag_list = serializers.ReadOnlyField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = ItemInfo
        fields = [
            'id', 'item_code', 'item_name', 'unit', 'perishability',
            'category', 'resource_type', 'activity_name', 'tags',
            'tag_list', 'active', 'item_count'
        ]
        swagger_schema_name = 'ItemInfo'          # <-- exact component name

    def get_item_count(self, obj):
        return obj.items.count()


class ItemAttributeSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item_info.item_name', read_only=True)

    class Meta:
        model = ItemAttribute
        fields = ['id', 'item_info', 'item_name', 'key', 'datatype']
        read_only_fields = ['id']
        extra_kwargs = {'item_info': {'required': True}}
        swagger_schema_name = 'ItemAttribute'     # <-- exact component name


class ItemInfoDetailSerializer(ItemInfoSerializer):
    attributes = ItemAttributeSerializer(many=True, read_only=True)

    class Meta(ItemInfoSerializer.Meta):
        fields = ItemInfoSerializer.Meta.fields + ['attributes']
        swagger_schema_name = 'ItemInfoDetail'    # <-- optional – distinguishes list vs detail