import uuid
from django.db import models
from django.db.models import Manager
from django.utils.text import slugify
from .managers import SoftDeletionManager


class SoftDeletionModel(models.Model):
    """
    Abstract model with soft deletion
    """
    is_active = models.BooleanField(default=True)

    objects = Manager()
    active_objects = SoftDeletionManager()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.is_active = False
        self.save()

    def restore(self) -> None:
        self.is_active = True
        self.save()


class UUIDModel(models.Model):
    """
    Abstract model for uuid
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        db_index=True,
        editable=False,
    )

    class Meta:
        abstract = True


class TimeStampModel(models.Model):
    """
    Abstract model with timestamp
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True
    )

    class Meta:
        abstract = True


class SlugModel(models.Model):
    slug = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        editable=False,
    )

    class Meta:
        abstract = True

    def generate_unique_slug(self, base_text: str) -> str:
        slug_base = slugify(base_text)[:90]
        if not slug_base:
            slug_base = str(self.id)[:8]

        slug = slug_base
        counter = 1

        while self.__class__.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1

        return slug


class BaseModel(
    UUIDModel,
    TimeStampModel,
    SoftDeletionModel
):
    """
    Base model for inheritance
    """
    class Meta:
        abstract = True
