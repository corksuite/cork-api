from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone as django_timezone

from apps.core.models import UUIDAuditModel


class UserManager(BaseUserManager):
    """Custom manager for email-based authentication."""

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", self._generate_username(email))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("status", User.Status.ACTIVE)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    @staticmethod
    def _generate_username(email: str) -> str:
        """Derive a unique username from the email local part."""
        from apps.identity.authentication.utils import generate_username_from_email

        return generate_username_from_email(email)


class User(UUIDAuditModel, AbstractBaseUser, PermissionsMixin):
    """
    Minimal authentication model.

    Profile and preference data live on UserProfile to keep auth concerns separate.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INVITED = "invited", "Invited"
        SUSPENDED = "suspended", "Suspended"
        DEACTIVATED = "deactivated", "Deactivated"

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.INVITED,
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=django_timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["email"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        if hasattr(self, "profile") and self.profile.display_name:
            return self.profile.display_name
        return self.email


class UserProfile(UUIDAuditModel):
    """Extended user profile — separate from authentication credentials."""

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        NON_BINARY = "non_binary", "Non-binary"
        PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to="users/avatars/", blank=True)
    bio = models.TextField(blank=True)
    language = models.CharField(max_length=32, default="en")
    timezone = models.CharField(max_length=64, default="UTC")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=32,
        choices=Gender.choices,
        blank=True,
    )
    job_title = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, blank=True)
    address = models.JSONField(default=dict, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    theme = models.CharField(max_length=32, default="system")
    accessibility_settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["user__email"]

    def __str__(self) -> str:
        return f"Profile for {self.user.email}"

    def get_full_name(self) -> str:
        return " ".join(part for part in [self.first_name, self.last_name] if part)
