import uuid
import secrets
import string
from django.db import models
from django.db.models import Manager
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

    def generate_unique_slug(self, base_text: str = None, length: int = 8) -> str:
        """
        Generate a unique random slug.
        Uses URL-safe characters (letters and digits).
        Default length is 8 characters (like YouTube: dQw4w9WgXcQ).
        """
        # Characters to use: a-z, A-Z, 0-9 (62 characters total)
        alphabet = string.ascii_letters + string.digits

        # Try to generate unique slug (max 10 attempts)
        for _ in range(10):
            # Generate random string
            slug = ''.join(secrets.choice(alphabet) for _ in range(length))

            # Check if unique
            if not self.__class__.objects.filter(slug=slug).exclude(id=self.id).exists():
                return slug

        # Fallback: use UUID if couldn't generate unique slug
        return str(uuid.uuid4())[:8]


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
