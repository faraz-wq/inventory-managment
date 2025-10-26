"""
Location Serializers
"""
from rest_framework import serializers
from .models import District, Mandal, Village


class DistrictSerializer(serializers.ModelSerializer):
    """
    Serializer for District model
    """
    mandal_count = serializers.SerializerMethodField()
    village_count = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = [
            'id', 'district_name', 'district_code_ap', 'district_code_ind',
            'is_active', 'mandal_count', 'village_count'
        ]

    def get_mandal_count(self, obj):
        """Count of mandals in this district"""
        return obj.mandals.count()

    def get_village_count(self, obj):
        """Count of villages in this district"""
        return obj.villages.count()


class MandalSerializer(serializers.ModelSerializer):
    """
    Serializer for Mandal model
    """
    district_name = serializers.CharField(source='district.district_name', read_only=True)
    village_count = serializers.SerializerMethodField()

    class Meta:
        model = Mandal
        fields = [
            'id', 'mandal_name', 'mandal_code_ap', 'mandal_code_ind',
            'district', 'district_name', 'is_active', 'village_count'
        ]

    def get_village_count(self, obj):
        """Count of villages in this mandal"""
        return obj.villages.count()


class VillageSerializer(serializers.ModelSerializer):
    """
    Serializer for Village model
    """
    mandal_name = serializers.CharField(source='mandal.mandal_name', read_only=True)
    district_name = serializers.CharField(source='district.district_name', read_only=True)

    class Meta:
        model = Village
        fields = [
            'id', 'village_name', 'village_code_ap', 'village_code_ind',
            'mandal', 'mandal_name', 'district', 'district_name', 'is_active'
        ]


class VillageDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Village with nested mandal and district info
    """
    mandal = MandalSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = Village
        fields = [
            'id', 'village_name', 'village_code_ap', 'village_code_ind',
            'mandal', 'district', 'is_active'
        ]
