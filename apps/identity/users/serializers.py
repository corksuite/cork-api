from rest_framework import serializers

from apps.identity.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "display_name",
            "avatar",
            "phone_number",
            "timezone",
            "locale",
            "preferred_language",
            "status",
            "email_verified",
            "phone_verified",
            "last_seen",
            "date_joined",
        ]
        read_only_fields = fields
