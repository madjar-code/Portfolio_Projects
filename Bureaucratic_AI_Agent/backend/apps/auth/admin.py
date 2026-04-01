from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "created_at",
    )
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "phone", "avatar")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "full_name", "password1", "password2")}),
    )
    search_fields = ("email", "full_name")
    filter_horizontal = ()
