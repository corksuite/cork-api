"""Authentication utility functions."""

from __future__ import annotations

import re
import uuid

from django.utils.text import slugify


def extract_email_local_part(email: str) -> str:
    """Return the local part of an email address."""
    return email.split("@")[0].strip().lower()


def generate_display_name_from_email(email: str) -> str:
    """
    Derive a human-readable display name from an email address.

    Example: john@example.com -> john
    """
    local_part = extract_email_local_part(email)
    # Use only alphanumeric segments for a clean default display name.
    cleaned = re.sub(r"[^a-z0-9]+", " ", local_part).strip()
    return cleaned.split()[0] if cleaned else local_part


def generate_username_from_email(email: str) -> str:
    """
    Generate a unique username from an email address.

    Django's auth system expects a username field even when authenticating
    with email; this keeps the User model compatible with admin and third-party
    packages while email remains the primary credential.
    """
    from apps.identity.users.models import User

    base = slugify(extract_email_local_part(email)).replace("-", "_") or "user"
    base = base[:140]
    username = base

    suffix = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}_{suffix}"
        suffix += 1

    return username


def generate_organization_name(display_name: str | None) -> str:
    """Build a personal workspace name for a newly registered user."""
    if display_name and display_name.strip():
        return f"{display_name.strip()} Workspace"
    return "My Workspace"


def generate_unique_slug(name: str) -> str:
    """Generate a URL-safe, unique organization slug."""
    from apps.identity.organizations.models import Organization

    base_slug = slugify(name)[:100] or "workspace"
    slug = base_slug

    while Organization.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

    return slug


DEFAULT_PROFILE_PREFERENCES: dict = {
    "notifications": {
        "email": True,
        "push": True,
        "in_app": True,
    },
    "privacy": {
        "show_online_status": True,
    },
}

DEFAULT_NOTIFICATION_SETTINGS: dict = {
    "email_digest": "daily",
    "mentions": True,
    "assignments": True,
}
