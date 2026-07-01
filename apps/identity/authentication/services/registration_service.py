"""User registration service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.identity.authentication.exceptions import EmailAlreadyExistsError
from apps.identity.authentication.repositories import (
    AuthProviderRepository,
    OrganizationRepository,
    UserRepository,
)
from apps.identity.authentication.services.jwt_service import JWTService
from apps.identity.authentication.utils import (
    DEFAULT_NOTIFICATION_SETTINGS,
    DEFAULT_PROFILE_PREFERENCES,
    generate_display_name_from_email,
    generate_organization_name,
    generate_unique_slug,
    generate_username_from_email,
)
from apps.identity.authentication.validators import validate_password_strength
from apps.identity.organizations.models import Organization, OrganizationMember
from apps.identity.users.models import User


@dataclass(frozen=True)
class RegistrationResult:
    """Structured result returned after successful registration."""

    user: User
    profile: Any
    organization: Organization
    membership: OrganizationMember
    tokens: dict[str, str]


class RegistrationService:
    """
    Orchestrate atomic user registration.

    All provisioning steps run inside a single transaction so partial
    registration never leaves orphaned records.
    """

    def __init__(
        self,
        user_repo: type[UserRepository] = UserRepository,
        org_repo: type[OrganizationRepository] = OrganizationRepository,
        auth_provider_repo: type[AuthProviderRepository] = AuthProviderRepository,
        jwt_service: type[JWTService] = JWTService,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.auth_provider_repo = auth_provider_repo
        self.jwt_service = jwt_service

    def register(
        self,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> RegistrationResult:
        """
        Register a new user with a personal organization workspace.

        Creates User, UserProfile, Organization, OrganizationMember,
        default preferences, and auth provider record in one transaction.
        """
        normalized_email = email.strip().lower()

        if self.user_repo.email_exists(normalized_email):
            raise EmailAlreadyExistsError()

        resolved_display_name = (
            display_name.strip()
            if display_name and display_name.strip()
            else generate_display_name_from_email(normalized_email)
        )

        validate_password_strength(password)

        with transaction.atomic():
            user = self.user_repo.create_user(
                email=normalized_email,
                password=password,
                username=generate_username_from_email(normalized_email),
                is_active=True,
                status=User.Status.ACTIVE,
                is_verified=False,
            )

            profile = self.user_repo.create_profile(
                user=user,
                display_name=resolved_display_name,
                preferences=DEFAULT_PROFILE_PREFERENCES.copy(),
                notification_settings=DEFAULT_NOTIFICATION_SETTINGS.copy(),
            )

            org_name = generate_organization_name(resolved_display_name)
            organization = self.org_repo.create_organization(
                name=org_name,
                slug=generate_unique_slug(org_name),
                owner=user,
                status=Organization.Status.ACTIVE,
                billing_email=normalized_email,
            )

            membership = self.org_repo.create_membership(
                organization=organization,
                user=user,
                role=OrganizationMember.Role.OWNER,
                status=OrganizationMember.Status.ACTIVE,
                joined_date=timezone.now(),
                invitation_accepted=True,
                primary_organization=True,
            )

            # Link password provider for future SSO/OAuth extensibility.
            self.auth_provider_repo.create_password_provider(user)

            tokens = self.jwt_service.generate_tokens(user)

        # Refresh relations for serialization outside the transaction block.
        user.refresh_from_db()
        profile.refresh_from_db()

        return RegistrationResult(
            user=user,
            profile=profile,
            organization=organization,
            membership=membership,
            tokens=tokens,
        )
