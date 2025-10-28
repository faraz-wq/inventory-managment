"""
Log Serializers
"""
from rest_framework import serializers
from .models import Log


class LogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Log
        fields = [
            'id', 'user', 'user_name', 'user_email', 'subject_type',
            'subject_id', 'action', 'status', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        swagger_schema_name = 'Log'   # exact component name in Swagger