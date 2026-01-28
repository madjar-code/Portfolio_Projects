from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.common.mixins.admin import BaseAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, BaseAdmin):
    """
    Admin interface for CustomUser model.
    """

    list_display = (
        "email",
        "name",
        "is_verified",
        "is_staff",
        "is_active",
        "oauth_provider",
        "created_at",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_verified",
        "oauth_provider",
        "created_at",
    )

    search_fields = (
        "email",
        "name",
        "oauth_id",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("email", "password")
        }),
        (_("Personal Info"), {
            "fields": ("name",)
        }),
        (_("OAuth Info"), {
            "fields": ("oauth_provider", "oauth_id"),
            "classes": ("collapse",),
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_verified",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        (_("Important Dates"), {
            "fields": ("last_login", "created_at", "updated_at"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "password1",
                "password2",
                "is_staff",
                "is_verified",
            ),
        }),
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "last_login",
    )
