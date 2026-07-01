"""JWT token management service."""

from __future__ import annotations

from typing import Any

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.identity.authentication.exceptions import TokenBlacklistError
from apps.identity.users.models import User


class JWTService:
    """Generate and manage JWT access/refresh tokens via SimpleJWT."""

    @staticmethod
    def generate_tokens(user: User) -> dict[str, str]:
        """Issue a fresh access/refresh token pair for the given user."""
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def blacklist_refresh_token(refresh_token: str) -> None:
        """Blacklist a refresh token to invalidate the session."""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            raise TokenBlacklistError(str(exc)) from exc

    @staticmethod
    def get_token_payload(user: User) -> dict[str, Any]:
        """Return token pair for embedding in auth responses."""
        return JWTService.generate_tokens(user)
