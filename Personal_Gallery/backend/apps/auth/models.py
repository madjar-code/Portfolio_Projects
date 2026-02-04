from typing import Optional
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.mixins.models import BaseModel, SlugModel
from .managers import CustomUserManager


class CustomUser(
    BaseModel,
    SlugModel,
    AbstractBaseUser,
    PermissionsMixin,
):
    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        help_text=_("Required. Unique email address for authentication."),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    name = models.CharField(
        _("name"),
        max_length=150,
        blank=True,
        help_text=_("User's display name."),
    )

    is_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether the user has verified their email address."),
    )

    oauth_provider = models.CharField(
        _("OAuth provider"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("OAuth provider name (e.g., 'google')."),
    )

    oauth_id = models.CharField(
        _("OAuth ID"),
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        help_text=_("Unique ID from OAuth provider."),
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["oauth_provider", "oauth_id"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        """String representation of the user."""
        return self.email

    def save(self, *args, **kwargs):
        if not self.slug:
            base_text = self.name or self.email.split('@')[0]
            self.slug = self.generate_unique_slug(base_text)
        super().save(*args, **kwargs)

    def is_email_user(self) -> bool:
        """
        Check if user registered via Email/Password.

        Returns:
            True if user uses email/password authentication
        """
        return not self.oauth_provider

    def is_oauth_user(self) -> bool:
        """
        Check if user registered via OAuth.

        Returns:
            True if user uses OAuth authentication
        """
        return bool(self.oauth_provider)

    def get_full_name(self) -> str:
        """
        Return the user's full name.

        Returns:
            User's name or email if name is not set
        """
        return self.name or self.email

    def get_short_name(self) -> str:
        """
        Return the user's short name.

        Returns:
            User's name or email if name is not set
        """
        return self.name or self.email
