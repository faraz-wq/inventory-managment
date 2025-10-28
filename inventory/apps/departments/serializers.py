"""
Department Serializers
"""
from rest_framework import serializers
from .models import Department, DepartmentContact


class DepartmentContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentContact
        fields = ['id', 'contact_type', 'contact_value']
        swagger_schema_name = 'DepartmentContact'   # exact component name


class DepartmentSerializer(serializers.ModelSerializer):
    contacts = DepartmentContactSerializer(many=True, read_only=True)
    contact_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'org_code', 'org_shortname', 'org_type', 'org_name',
            'report_org', 'agency_address', 'contact_person_name',
            'contact_person_designation', 'contact_person_address',
            'pin_code', 'active', 'contacts', 'contact_count'
        ]
        swagger_schema_name = 'Department'          # exact component name

    def get_contact_count(self, obj):
        return obj.contacts.count()


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            'org_code', 'org_shortname', 'org_type', 'org_name',
            'report_org', 'agency_address', 'contact_person_name',
            'contact_person_designation', 'contact_person_address',
            'pin_code', 'active'
        ]
        swagger_schema_name = 'DepartmentCreate'    # distinguishes create payload