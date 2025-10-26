"""
Department Serializers
"""
from rest_framework import serializers
from .models import Department, DepartmentContact


class DepartmentContactSerializer(serializers.ModelSerializer):
    """
    Serializer for DepartmentContact model
    """
    class Meta:
        model = DepartmentContact
        fields = ['id', 'contact_type', 'contact_value']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model with nested contacts
    """
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

    def get_contact_count(self, obj):
        """Count of contacts for this department"""
        return obj.contacts.count()


class DepartmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating departments
    """
    class Meta:
        model = Department
        fields = [
            'org_code', 'org_shortname', 'org_type', 'org_name',
            'report_org', 'agency_address', 'contact_person_name',
            'contact_person_designation', 'contact_person_address',
            'pin_code', 'active'
        ]
