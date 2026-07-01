"""Email-based authentication backend."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.backends import ModelBackend

from apps.identity.users.models import User


class EmailAuthenticationBackend(ModelBackend):
    """
    Authenticate users by email address instead of username.

    This backend allows `authenticate(request, email=..., password=...)` while
    remaining compatible with Django's admin and permission checks.
    """

    def authenticate(
        self,
        request: Any,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> User | None:
        email = kwargs.get("email") or username
        if email is None or password is None:
            return None

        try:
            user = User.objects.select_related("profile").get(
                email__iexact=email,
                deleted_at__isnull=True,
            )
        except User.DoesNotExist:
            # Run the hasher to mitigate timing attacks.
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id: Any) -> User | None:
        try:
            return User.objects.get(pk=user_id, deleted_at__isnull=True)
        except User.DoesNotExist:
            return None
