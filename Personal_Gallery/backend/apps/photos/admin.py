from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from apps.common.mixins.admin import BaseAdmin
from .models import Entry, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ("file", "preview", "is_active")
    readonly_fields = ("preview", "file_size", "width", "height")

    def preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 4px; object-fit: cover;" />',
                obj.file.url
            )
        return "-"

    preview.short_description = _("Preview")


@admin.register(Entry)
class EntryAdmin(BaseAdmin):
    list_display = (
        "title",
        "user",
        "photo_count",
        "is_active",
        "created_at",
        "updated_at",
    )
    
    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
        "user",
    )
    
    search_fields = (
        "title",
        "description",
        "user__email",
        "user__name",
    )
    
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {
            "fields": ("user", "title", "description")
        }),
        (_("Status"), {
            "fields": ("is_active",),
        }),
        (_("Timestamps"), {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    
    inlines = [PhotoInline]
    
    def photo_count(self, obj):
        return obj.photos.count()

    photo_count.short_description = _("Photos")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user").prefetch_related("photos")


@admin.register(Photo)
class PhotoAdmin(BaseAdmin):
    list_display = (
        "id",
        "preview_thumbnail",
        "entry",
        "user",
        "dimensions",
        "file_size_display_admin",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
        "entry",
        "user",
    )

    search_fields = (
        "entry__title",
        "user__email",
        "user__name",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("entry", "user", "file")
        }),
        (_("File Information"), {
            "fields": ("preview_image", "file_size_display_admin", "dimensions_display_admin"),
        }),
        (_("Status"), {
            "fields": ("is_active",),
        }),
        (_("Timestamps"), {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "preview_image",
        "file_size_display_admin",
        "dimensions_display_admin",
    )

    def preview_thumbnail(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px; object-fit: cover;" />',
                obj.file.url
            )
        return "-"

    preview_thumbnail.short_description = _("Preview")

    def preview_image(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 600px; border: 1px solid #ddd; padding: 5px; border-radius: 4px;" />',
                obj.file.url
            )
        return "-"

    preview_image.short_description = _("Image Preview")

    def dimensions(self, obj):
        return f"{obj.width} × {obj.height}"

    dimensions.short_description = _("Dimensions")

    def dimensions_display_admin(self, obj):
        return obj.dimensions_display

    dimensions_display_admin.short_description = _("Dimensions")

    def file_size_display_admin(self, obj):
        return obj.file_size_display

    file_size_display_admin.short_description = _("File Size")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("entry", "user")
