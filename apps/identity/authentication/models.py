import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import UUIDAuditModel


class AuthProviderAccount(UUIDAuditModel):
    class Provider(models.TextChoices):
        PASSWORD = "password", "Password"
        GOOGLE = "google", "Google"
        MICROSOFT = "microsoft", "Microsoft"
        GITHUB = "github", "GitHub"
        SAML = "saml", "SAML"
        OIDC = "oidc", "OIDC"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auth_provider_accounts",
    )
    provider = models.CharField(max_length=32, choices=Provider.choices)
    provider_user_id = models.CharField(max_length=255, blank=True)
    provider_email = models.EmailField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    connected_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["user__email", "provider"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_user_id"],
                condition=~models.Q(provider_user_id=""),
                name="unique_auth_provider_user_id",
            )
        ]

    def __str__(self):
        return f"{self.user} via {self.provider}"


class MFAMethod(UUIDAuditModel):
    class MethodType(models.TextChoices):
        TOTP = "totp", "Authenticator app"
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        WEBAUTHN = "webauthn", "Security key"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_methods",
    )
    method_type = models.CharField(max_length=32, choices=MethodType.choices)
    name = models.CharField(max_length=120, blank=True)
    secret = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["user__email", "method_type"]

    def __str__(self):
        return f"{self.method_type} for {self.user}"


class MagicLinkToken(UUIDAuditModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="magic_link_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_valid(self):
        return self.used_at is None and timezone.now() < self.expires_at

    def __str__(self):
        return f"Magic link for {self.user}"


class PasskeyCredential(UUIDAuditModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="passkey_credentials",
    )
    credential_id = models.CharField(max_length=512, unique=True)
    public_key = models.TextField()
    sign_count = models.PositiveIntegerField(default=0)
    device_name = models.CharField(max_length=120, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["user__email", "device_name"]

    def __str__(self):
        return self.device_name or f"Passkey for {self.user}"
