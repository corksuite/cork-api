import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import UUIDAuditModel


class Organization(UUIDAuditModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRIALING = "trialing", "Trialing"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    class DeploymentType(models.TextChoices):
        CLOUD = "cloud", "Cloud"
        ENTERPRISE = "enterprise", "Enterprise"
        SELF_HOSTED = "self_hosted", "Self hosted"
        GOVERNMENT = "government", "Government"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120, unique=True)
    logo = models.ImageField(upload_to="organizations/logos/", blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=2, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.TRIALING,
    )
    subscription = models.CharField(max_length=120, blank=True)
    billing_email = models.EmailField(blank=True)
    maximum_users = models.PositiveIntegerField(default=10)
    deployment_type = models.CharField(
        max_length=32,
        choices=DeploymentType.choices,
        default=DeploymentType.CLOUD,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name


class OrganizationMember(UUIDAuditModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        GUEST = "guest", "Guest"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INVITED = "invited", "Invited"
        SUSPENDED = "suspended", "Suspended"
        LEFT = "left", "Left"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.INVITED,
    )
    joined_date = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organization_members_invited",
    )
    invitation_accepted = models.BooleanField(default=False)
    last_active = models.DateTimeField(null=True, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, blank=True)
    primary_organization = models.BooleanField(default=False)

    class Meta:
        ordering = ["organization__name", "user__email"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_user_organization_membership",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["user", "primary_organization"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.organization}"


class OrganizationInvitation(UUIDAuditModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=32,
        choices=OrganizationMember.Role.choices,
        default=OrganizationMember.Role.MEMBER,
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    accepted = models.BooleanField(default=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organization_invitations_sent",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "email"],
                condition=models.Q(accepted=False),
                name="unique_pending_organization_invitation",
            )
        ]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.email} invitation to {self.organization}"


class Team(UUIDAuditModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    members = models.ManyToManyField(
        OrganizationMember,
        blank=True,
        related_name="teams",
    )

    class Meta:
        ordering = ["organization__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_team_slug_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.organization}: {self.name}"
