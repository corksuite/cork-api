from django.db import models

from apps.core.models import UUIDAuditModel
from apps.identity.organizations.models import Organization


class Permission(UUIDAuditModel):
    code = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    resource = models.CharField(max_length=120)
    action = models.CharField(max_length=80)

    class Meta:
        ordering = ["resource", "action"]
        indexes = [
            models.Index(fields=["resource", "action"]),
        ]

    def __str__(self):
        return self.code


class Role(UUIDAuditModel):
    class Scope(models.TextChoices):
        SYSTEM = "system", "System"
        ORGANIZATION = "organization", "Organization"
        WORKSPACE = "workspace", "Workspace"
        PROJECT = "project", "Project"

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True)
    scope = models.CharField(
        max_length=32,
        choices=Scope.choices,
        default=Scope.ORGANIZATION,
    )
    is_system = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        blank=True,
        related_name="roles",
    )

    class Meta:
        ordering = ["organization__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_role_slug_per_organization",
            )
        ]

    def __str__(self):
        return self.name


class RolePermission(UUIDAuditModel):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    class Meta:
        ordering = ["role__name", "permission__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_permission_per_role",
            )
        ]

    def __str__(self):
        return f"{self.role}: {self.permission}"
