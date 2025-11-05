"""
User Serializers 
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserRole
from apps.rbac.serializers import RoleSerializer

User = get_user_model()


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.rbac.models', fromlist=['Role']).Role.objects.all(),
        source='role',
        write_only=True
    )

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'role_id']
        swagger_schema_name = 'UserRole'


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    dept_shortname = serializers.CharField(source='dept.org_shortname', read_only=True)
    location_name = serializers.CharField(source='location.village_name', read_only=True)
    geocode_name = serializers.SerializerMethodField(read_only=True)
    geocode_codes = serializers.SerializerMethodField(read_only=True)
    dept_name = serializers.CharField(source='dept.org_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'staff_id', 'name', 'email', 'profile_picture', 'id_picture',
            'phone_no', 'active', 'dept', 'dept_name', 'dept_shortname', 'location', 'location_name',
            'cfms_ref', 'verified_status', 'created_at', 'updated_at',
            'geocode_name', 'geocode_codes',
            'last_login', 'roles'
        ]
        read_only_fields = ['staff_id', 'created_at', 'updated_at', 'last_login']
        swagger_schema_name = 'User'

    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj).select_related('role')
        return RoleSerializer([ur.role for ur in user_roles], many=True).data

    def get_geocode_name(self, obj):
        """Return geocode name as 'village, mandal, district' when available for the user's location."""
        geocode = getattr(obj, 'location', None)
        if not geocode:
            return ''

        parts = []
        village = getattr(geocode, 'village_name', None)
        if village:
            parts.append(village)

        mandal = getattr(geocode, 'mandal', None)
        mandal_name = None
        if mandal:
            mandal_name = getattr(mandal, 'mandal_name', None)
        else:
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
        """Return geocode AP codes as a dictionary for the user's location.

        Returns dict with keys: district_code_ap, mandal_code_ap, village_code_ap
        Any missing code will be None.
        """
        geocode = getattr(obj, 'location', None)
        if not geocode:
            return {
                'district_code_ap': None,
                'mandal_code_ap': None,
                'village_code_ap': None
            }

        # District code
        district = getattr(geocode, 'district', None)
        district_code = None
        if district:
            district_code = getattr(district, 'district_code_ap', None)
        if not district_code:
            district_code = getattr(geocode, 'district_code_ap', None)

        # Mandal code
        mandal = getattr(geocode, 'mandal', None)
        mandal_code = None
        if mandal:
            mandal_code = getattr(mandal, 'mandal_code_ap', None)
        if not mandal_code:
            mandal_code = getattr(geocode, 'mandal_code_ap', None)

        # Village code
        village_code = getattr(geocode, 'village_code_ap', None)

        return {
            'district_code_ap': district_code,
            'mandal_code_ap': mandal_code,
            'village_code_ap': village_code
        }


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'name', 'email', 'password', 'profile_picture', 'id_picture',
            'phone_no', 'dept', 'location', 'cfms_ref', 'verified_status'
        ]
        swagger_schema_name = 'UserCreate'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'name', 'profile_picture', 'id_picture', 'phone_no',
            'dept', 'location', 'cfms_ref', 'verified_status', 'active'
        ]
        swagger_schema_name = 'UserUpdate'


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})

    swagger_schema_name = 'ChangePassword'

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.rbac.models', fromlist=['Role']).Role.objects.all()
    )

    swagger_schema_name = 'AssignRole'

    def create(self, validated_data):
        user = self.context.get('user')
        role = validated_data['role_id']
        user_role, created = UserRole.objects.get_or_create(user=user, role=role)
        return user_role