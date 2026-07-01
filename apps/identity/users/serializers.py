from rest_framework import serializers

from apps.identity.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Read-only user list serializer for admin endpoints."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "is_active",
            "is_verified",
            "status",
            "last_login",
            "date_joined",
            "created_at",
        ]
        read_only_fields = fields
