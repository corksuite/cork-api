"""User login service."""

from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import authenticate

from apps.identity.authentication.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
)
from apps.identity.authentication.repositories import OrganizationRepository
from apps.identity.authentication.services.jwt_service import JWTService
from apps.identity.organizations.models import Organization, OrganizationMember
from apps.identity.users.models import User


@dataclass(frozen=True)
class LoginResult:
    """Structured result returned after successful login."""

    user: User
    profile: object
    organizations: list[Organization]
    membership: OrganizationMember | None
    current_organization: Organization | None
    tokens: dict[str, str]


class LoginService:
    """Authenticate a user by email and issue JWT tokens."""

    def __init__(
        self,
        org_repo: type[OrganizationRepository] = OrganizationRepository,
        jwt_service: type[JWTService] = JWTService,
    ):
        self.org_repo = org_repo
        self.jwt_service = jwt_service

    def login(self, email: str, password: str) -> LoginResult:
        """Validate credentials and return the full authentication payload."""
        normalized_email = email.strip().lower()

        user = authenticate(email=normalized_email, password=password)
        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active or user.status != User.Status.ACTIVE:
            raise InactiveUserError()

        memberships = self.org_repo.get_user_memberships(user)
        organizations = [membership.organization for membership in memberships]
        primary_membership = self.org_repo.get_primary_membership(user)

        if primary_membership is None and memberships:
            primary_membership = memberships[0]

        current_organization = (
            primary_membership.organization if primary_membership else None
        )

        profile = getattr(user, "profile", None)
        tokens = self.jwt_service.generate_tokens(user)

        return LoginResult(
            user=user,
            profile=profile,
            organizations=organizations,
            membership=primary_membership,
            current_organization=current_organization,
            tokens=tokens,
        )
