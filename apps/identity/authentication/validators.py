"""Custom validators for authentication flows."""

from __future__ import annotations

import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.identity.users.models import User


class PasswordStrengthValidator:
    """
    Enforce enterprise-grade password rules on top of Django defaults.

    Requires at least one uppercase letter, one lowercase letter, one digit,
    and one special character in addition to Django's built-in validators.
    """

    SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*(),.?\":{}|<>_\-\[\]\\;/+=~`]")

    def validate(self, password: str, user: User | None = None) -> None:
        validate_password(password, user=user)

        errors: list[str] = []
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit.")
        if not self.SPECIAL_CHAR_PATTERN.search(password):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise DjangoValidationError(errors)

    def get_help_text(self) -> str:
        return (
            "Password must contain uppercase and lowercase letters, "
            "a digit, and a special character."
        )


def validate_password_strength(password: str, user: User | None = None) -> None:
    """Validate password strength using Django and custom rules."""
    PasswordStrengthValidator().validate(password, user=user)
