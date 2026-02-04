from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from PIL import Image as PILImage

from apps.common.mixins.models import BaseModel, SlugModel


class Entry(BaseModel, SlugModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name=_("owner"),
        help_text=_("The user who owns this entry."),
    )

    title = models.CharField(
        _("title"),
        max_length=255,
        help_text=_("Entry title (required)."),
    )

    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
        help_text=_("Optional description or caption for the entry."),
    )

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")
        db_table = "entries"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)


def photo_upload_path(instance, filename):
    user_slug = instance.user.slug if hasattr(instance.user, 'slug') else str(instance.user.id)[:8]
    entry_slug = instance.entry.slug if hasattr(instance.entry, 'slug') else str(instance.entry.id)[:8]
    return f"photos/{user_slug}/{entry_slug}/{filename}"


class Photo(BaseModel):
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name=_("entry"),
        help_text=_("The entry this photo belongs to."),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name=_("owner"),
        help_text=_("Denormalized FK for efficient filtering by user."),
    )

    file = models.ImageField(
        _("image file"),
        upload_to=photo_upload_path,
        max_length=500,
        help_text=_("Upload an image file (JPEG, PNG, WebP)."),
        null=True,
        blank=True,
    )

    file_size = models.PositiveIntegerField(
        _("file size"),
        help_text=_("File size in bytes."),
        editable=False,
        default=0,
    )

    width = models.PositiveIntegerField(
        _("width"),
        help_text=_("Image width in pixels."),
        editable=False,
        default=0,
    )

    height = models.PositiveIntegerField(
        _("height"),
        help_text=_("Image height in pixels."),
        editable=False,
        default=0,
    )

    class Meta:
        verbose_name = _("photo")
        verbose_name_plural = _("photos")
        db_table = "photos"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Photo {self.id} in {self.entry.title}"

    def save(self, *args, **kwargs):
        if not self.user_id and self.entry_id:
            self.user_id = self.entry.user_id

        if self.file:
            self.file_size = self.file.size

            try:
                with PILImage.open(self.file) as image:
                    self.width, self.height = image.size
            except Exception:
                self.width = 0
                self.height = 0

        super().save(*args, **kwargs)

    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return None

    @property
    def file_size_display(self):
        if not self.file_size:
            return "0 KB"

        size_kb = self.file_size / 1024
        if size_kb < 1024:
            return f"{size_kb:.1f} KB"

        size_mb = size_kb / 1024
        return f"{size_mb:.2f} MB"

    @property
    def dimensions_display(self):
        return f"{self.width} × {self.height} px"
