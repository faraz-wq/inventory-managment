"""
Location Serializers – Swagger-ready
"""
from rest_framework import serializers
from .models import District, Mandal, Village


class DistrictSerializer(serializers.ModelSerializer):
    mandal_count = serializers.SerializerMethodField()
    village_count = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = [
            'id', 'district_name', 'district_code_ap', 'district_code_ind',
            'is_active', 'mandal_count', 'village_count'
        ]
        swagger_schema_name = 'District'          # exact component name

    def get_mandal_count(self, obj):
        return obj.mandals.count()

    def get_village_count(self, obj):
        return obj.villages.count()


class MandalSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.district_name', read_only=True)
    village_count = serializers.SerializerMethodField()

    class Meta:
        model = Mandal
        fields = [
            'id', 'mandal_name', 'mandal_code_ap', 'mandal_code_ind',
            'district', 'district_name', 'is_active', 'village_count'
        ]
        swagger_schema_name = 'Mandal'            # exact component name

    def get_village_count(self, obj):
        return obj.villages.count()


class VillageSerializer(serializers.ModelSerializer):
    mandal_name = serializers.CharField(source='mandal.mandal_name', read_only=True)
    district_name = serializers.CharField(source='district.district_name', read_only=True)

    class Meta:
        model = Village
        fields = [
            'id', 'village_name', 'village_code_ap', 'village_code_ind',
            'mandal', 'mandal_name', 'district', 'district_name', 'is_active'
        ]
        swagger_schema_name = 'Village'           # exact component name


class VillageDetailSerializer(serializers.ModelSerializer):
    mandal = MandalSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = Village
        fields = [
            'id', 'village_name', 'village_code_ap', 'village_code_ind',
            'mandal', 'district', 'is_active'
        ]
        swagger_schema_name = 'VillageDetail'     # distinguishes list vs detail