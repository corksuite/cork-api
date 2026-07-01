"""Data access layer for authentication-related entities."""

from __future__ import annotations

from apps.identity.authentication.models import AuthProviderAccount
from apps.identity.organizations.models import Organization, OrganizationMember
from apps.identity.users.models import User, UserProfile


class UserRepository:
    """Repository for User and UserProfile persistence."""

    @staticmethod
    def email_exists(email: str) -> bool:
        return User.objects.filter(email__iexact=email, deleted_at__isnull=True).exists()

    @staticmethod
    def create_user(**kwargs) -> User:
        return User.objects.create_user(**kwargs)

    @staticmethod
    def create_profile(**kwargs) -> UserProfile:
        return UserProfile.objects.create(**kwargs)

    @staticmethod
    def get_by_email(email: str) -> User | None:
        try:
            return User.objects.select_related("profile").get(
                email__iexact=email,
                deleted_at__isnull=True,
            )
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(user_id) -> User | None:
        try:
            return User.objects.select_related("profile").get(
                pk=user_id,
                deleted_at__isnull=True,
            )
        except User.DoesNotExist:
            return None


class OrganizationRepository:
    """Repository for organization provisioning during registration."""

    @staticmethod
    def create_organization(**kwargs) -> Organization:
        return Organization.objects.create(**kwargs)

    @staticmethod
    def create_membership(**kwargs) -> OrganizationMember:
        return OrganizationMember.objects.create(**kwargs)

    @staticmethod
    def get_user_memberships(user: User) -> list[OrganizationMember]:
        return list(
            OrganizationMember.objects.select_related("organization")
            .filter(
                user=user,
                status=OrganizationMember.Status.ACTIVE,
                deleted_at__isnull=True,
            )
            .order_by("-primary_organization", "organization__name")
        )

    @staticmethod
    def get_primary_membership(user: User) -> OrganizationMember | None:
        return (
            OrganizationMember.objects.select_related("organization")
            .filter(
                user=user,
                status=OrganizationMember.Status.ACTIVE,
                primary_organization=True,
                deleted_at__isnull=True,
            )
            .first()
        )


class AuthProviderRepository:
    """Repository for linked authentication providers."""

    @staticmethod
    def create_password_provider(user: User) -> AuthProviderAccount:
        return AuthProviderAccount.objects.create(
            user=user,
            provider=AuthProviderAccount.Provider.PASSWORD,
            provider_user_id=str(user.id),
            provider_email=user.email,
        )
