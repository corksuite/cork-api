"""Authentication-specific exceptions."""

from __future__ import annotations


class AuthenticationError(Exception):
    """Base class for authentication failures."""

    default_message = "Authentication failed."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class InvalidCredentialsError(AuthenticationError):
    default_message = "Invalid email or password."


class EmailAlreadyExistsError(AuthenticationError):
    default_message = "A user with this email already exists."


class InactiveUserError(AuthenticationError):
    default_message = "This account is inactive."


class TokenBlacklistError(AuthenticationError):
    default_message = "Unable to blacklist the refresh token."
