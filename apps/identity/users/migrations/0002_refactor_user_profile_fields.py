"""Refactor User/Profile separation for authentication module."""

from __future__ import annotations

from django.db import migrations, models
from django.utils.text import slugify


def migrate_profile_fields_forward(apps, schema_editor):
    """Move profile-oriented data from User onto UserProfile."""
    User = apps.get_model("users", "User")
    UserProfile = apps.get_model("users", "UserProfile")

    for user in User.objects.all().iterator():
        profile, _ = UserProfile.objects.get_or_create(user=user)

        if not profile.display_name and user.display_name:
            profile.display_name = user.display_name
        if not profile.first_name and user.first_name:
            profile.first_name = user.first_name
        if not profile.last_name and user.last_name:
            profile.last_name = user.last_name
        if not profile.phone and user.phone_number:
            profile.phone = user.phone_number
        if not profile.avatar and user.avatar:
            profile.avatar = user.avatar
        if profile.timezone == "UTC" and user.timezone and user.timezone != "UTC":
            profile.timezone = user.timezone
        if profile.language == "en" and user.preferred_language:
            profile.language = user.preferred_language

        profile.save()


def populate_usernames(apps, schema_editor):
    """Ensure every user has a unique username before enforcing uniqueness."""
    User = apps.get_model("users", "User")

    for user in User.objects.all().iterator():
        if user.username:
            continue

        local_part = user.email.split("@")[0].strip().lower()
        base = slugify(local_part).replace("-", "_") or "user"
        base = base[:140]
        username = base
        suffix = 1

        while User.objects.filter(username=username).exclude(pk=user.pk).exists():
            username = f"{base}_{suffix}"
            suffix += 1

        user.username = username
        user.save(update_fields=["username"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="email_verified",
            new_name="is_verified",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="birth_date",
            new_name="date_of_birth",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="avatar",
            field=models.ImageField(blank=True, upload_to="users/avatars/"),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="display_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="first_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("non_binary", "Non-binary"),
                    ("prefer_not_to_say", "Prefer not to say"),
                    ("other", "Other"),
                ],
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="language",
            field=models.CharField(default="en", max_length=32),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="last_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="phone",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="timezone",
            field=models.CharField(default="UTC", max_length=64),
        ),
        migrations.RunPython(migrate_profile_fields_forward, migrations.RunPython.noop),
        migrations.RunPython(populate_usernames, migrations.RunPython.noop),
        migrations.RemoveField(model_name="user", name="avatar"),
        migrations.RemoveField(model_name="user", name="display_name"),
        migrations.RemoveField(model_name="user", name="first_name"),
        migrations.RemoveField(model_name="user", name="last_name"),
        migrations.RemoveField(model_name="user", name="last_login_ip"),
        migrations.RemoveField(model_name="user", name="last_seen"),
        migrations.RemoveField(model_name="user", name="locale"),
        migrations.RemoveField(model_name="user", name="phone_number"),
        migrations.RemoveField(model_name="user", name="phone_verified"),
        migrations.RemoveField(model_name="user", name="preferred_language"),
        migrations.RemoveField(model_name="user", name="timezone"),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["username"], name="users_user_usernam_idx"),
        ),
    ]
