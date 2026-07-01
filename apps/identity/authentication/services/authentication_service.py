"""Authentication orchestration and session context service."""

from __future__ import annotations

from dataclasses import dataclass

from apps.identity.authentication.repositories import OrganizationRepository
from apps.identity.authentication.services.jwt_service import JWTService
from apps.identity.organizations.models import Organization, OrganizationMember
from apps.identity.users.models import User

# Role-based permission codes returned by /me until full RBAC assignment exists.
ROLE_PERMISSIONS: dict[str, list[str]] = {
    OrganizationMember.Role.OWNER: [
        "organization.manage",
        "organization.delete",
        "members.invite",
        "members.manage",
        "members.remove",
        "billing.manage",
        "settings.manage",
    ],
    OrganizationMember.Role.ADMIN: [
        "organization.manage",
        "members.invite",
        "members.manage",
        "settings.manage",
    ],
    OrganizationMember.Role.MEMBER: [
        "organization.view",
        "members.view",
    ],
    OrganizationMember.Role.GUEST: [
        "organization.view",
    ],
}


@dataclass(frozen=True)
class MeResult:
    """Structured result for the authenticated /me endpoint."""

    user: User
    profile: object | None
    organizations: list[Organization]
    membership: OrganizationMember | None
    role: str | None
    permissions: list[str]
    current_organization: Organization | None


class AuthenticationService:
    """Resolve authenticated user context for protected endpoints."""

    def __init__(
        self,
        org_repo: type[OrganizationRepository] = OrganizationRepository,
        jwt_service: type[JWTService] = JWTService,
    ):
        self.org_repo = org_repo
        self.jwt_service = jwt_service

    def get_me_context(self, user: User) -> MeResult:
        """Build the full authenticated user context."""
        memberships = self.org_repo.get_user_memberships(user)
        organizations = [membership.organization for membership in memberships]
        primary_membership = self.org_repo.get_primary_membership(user)

        if primary_membership is None and memberships:
            primary_membership = memberships[0]

        role = primary_membership.role if primary_membership else None
        permissions = ROLE_PERMISSIONS.get(role, []) if role else []
        current_organization = (
            primary_membership.organization if primary_membership else None
        )

        profile = getattr(user, "profile", None)

        return MeResult(
            user=user,
            profile=profile,
            organizations=organizations,
            membership=primary_membership,
            role=role,
            permissions=permissions,
            current_organization=current_organization,
        )

    def logout(self, refresh_token: str) -> None:
        """Invalidate the user's refresh token."""
        self.jwt_service.blacklist_refresh_token(refresh_token)
