"""Authentication and identity serializers."""

from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.identity.authentication.validators import validate_password_strength
from apps.identity.organizations.models import Organization, OrganizationMember
from apps.identity.users.models import User, UserProfile


class RegisterSerializer(serializers.Serializer):
    """Validate registration input."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    display_name = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_password(self, value: str) -> str:
        try:
            validate_password_strength(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value


class LoginSerializer(serializers.Serializer):
    """Validate login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class LogoutSerializer(serializers.Serializer):
    """Validate logout refresh token payload."""

    refresh = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Minimal user representation — authentication fields only."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "is_active",
            "is_verified",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    """User profile representation."""

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "display_name",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "bio",
            "language",
            "timezone",
            "date_of_birth",
            "gender",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrganizationSummarySerializer(serializers.ModelSerializer):
    """Compact organization payload for auth responses."""

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "status",
            "timezone",
            "created_at",
        ]
        read_only_fields = fields


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Membership details including role within an organization."""

    organization = OrganizationSummarySerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            "id",
            "organization",
            "role",
            "status",
            "primary_organization",
            "joined_date",
        ]
        read_only_fields = fields


class AuthTokensSerializer(serializers.Serializer):
    """JWT token pair."""

    access = serializers.CharField()
    refresh = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    """Shared auth response shape for register and login."""

    user = UserSerializer()
    profile = ProfileSerializer(allow_null=True)
    organizations = OrganizationSummarySerializer(many=True)
    membership = OrganizationMembershipSerializer(allow_null=True)
    current_organization = OrganizationSummarySerializer(allow_null=True)
    tokens = AuthTokensSerializer()


class MeSerializer(serializers.Serializer):
    """Authenticated user context for /me."""

    user = UserSerializer()
    profile = ProfileSerializer(allow_null=True)
    organizations = OrganizationSummarySerializer(many=True)
    membership = OrganizationMembershipSerializer(allow_null=True)
    role = serializers.CharField(allow_null=True)
    permissions = serializers.ListField(child=serializers.CharField())
    current_organization = OrganizationSummarySerializer(allow_null=True)
