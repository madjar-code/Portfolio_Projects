from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.photos.models import Entry, Photo
from apps.photos.exceptions import (
    InvalidPhotoFormatError,
    PhotoSizeTooLargeError,
    MaxPhotosExceededError,
)


class PhotoDetailSerializer(ModelSerializer):
    """Serializer for photo details with entry info."""
    file_url = serializers.SerializerMethodField()
    entry_title = serializers.CharField(source="entry.title", read_only=True)
    entry_slug = serializers.CharField(source="entry.slug", read_only=True)

    class Meta:
        model = Photo
        fields = (
            "id",
            "entry",
            "entry_title",
            "entry_slug",
            "file_url",
            "file_size",
            "width",
            "height",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "file_size",
            "width",
            "height",
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj: Photo) -> str:
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return ""


class EntryListSerializer(ModelSerializer):
    photo_count = serializers.SerializerMethodField()
    first_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "photo_count",
            "first_photo_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_photo_count(self, obj: Entry) -> int:
        return obj.photos.filter(is_active=True).count()

    def get_first_photo_url(self, obj: Entry) -> str:
        request = self.context.get("request")
        first_photo = obj.photos.filter(is_active=True).first()
        if first_photo and first_photo.file and request:
            return request.build_absolute_uri(first_photo.file.url)
        return ""


class EntryDetailSerializer(ModelSerializer):
    photo_count = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "photo_count",
            "photos",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def get_photo_count(self, obj: Entry) -> int:
        """Return count of active photos in this entry."""
        return obj.photos.filter(is_active=True).count()

    def get_photos(self, obj: Entry):
        active_photos = obj.photos.filter(is_active=True)
        return PhotoDetailSerializer(active_photos, many=True, context=self.context).data


class EntryCreateSerializer(ModelSerializer):
    """Serializer for creating a new entry without photos."""

    class Meta:
        model = Entry
        fields = ("title", "description")

    def create(self, validated_data):
        """Create entry and assign current user as owner."""
        user = self.context["request"].user
        return Entry.objects.create(user=user, **validated_data)

    def to_representation(self, instance):
        """Return detailed representation after creation."""
        return EntryDetailSerializer(instance, context=self.context).data


class EntryUpdateSerializer(ModelSerializer):
    """Serializer for updating entry title and description."""

    class Meta:
        model = Entry
        fields = ("title", "description")

    def to_representation(self, instance):
        """Return detailed representation after update."""
        return EntryDetailSerializer(instance, context=self.context).data


class PhotoListSerializer(ModelSerializer):
    file_url = serializers.SerializerMethodField()
    entry_title = serializers.CharField(source="entry.title", read_only=True)

    class Meta:
        model = Photo
        fields = (
            "id",
            "entry_title",
            "file_url",
            "file_size",
            "width",
            "height",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj: Photo) -> str:
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return ""


class PhotoSerializer(ModelSerializer):
    """Serializer for creating photos associated with an entry."""

    # Configuration constants
    MAX_PHOTOS_PER_ENTRY = 50
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FORMATS = ["JPEG", "PNG", "WEBP"]

    class Meta:
        model = Photo
        fields = (
            "id",
            "entry",
            "file",
            "file_size",
            "width",
            "height",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "file_size",
            "width",
            "height",
            "created_at",
            "updated_at"
        )

    def validate_entry(self, value):
        """Validate that the entry belongs to the current user."""
        request = self.context.get("request")
        if request and value.user != request.user:
            raise serializers.ValidationError(
                "You can only add photos to your own entries"
            )

        # Check max photos limit
        current_photo_count = value.photos.filter(is_active=True).count()
        if current_photo_count >= self.MAX_PHOTOS_PER_ENTRY:
            raise MaxPhotosExceededError(
                f"Entry already has {current_photo_count} photos. "
                f"Maximum allowed is {self.MAX_PHOTOS_PER_ENTRY}."
            )

        return value

    def validate_file(self, value):
        """Validate photo file format and size."""
        if not value:
            raise serializers.ValidationError("Photo file is required")

        # Check file size
        max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if value.size > max_size_bytes:
            raise PhotoSizeTooLargeError(
                f"Photo size ({value.size / (1024 * 1024):.2f}MB) exceeds "
                f"the maximum allowed limit of {self.MAX_FILE_SIZE_MB}MB"
            )

        # Check file format
        file_extension = value.name.split(".")[-1].upper()
        if file_extension not in self.ALLOWED_FORMATS:
            raise InvalidPhotoFormatError(
                f"Invalid photo format '{file_extension}'. "
                f"Allowed formats: {', '.join(self.ALLOWED_FORMATS)}"
            )

        return value


class PhotoUpdateSerializer(ModelSerializer):
    """Serializer for updating photo (moving to another entry)."""

    class Meta:
        model = Photo
        fields = ("entry",)

    def validate_entry(self, value):
        """Validate that the new entry belongs to the current user."""
        request = self.context.get("request")
        if request and value.user != request.user:
            raise serializers.ValidationError(
                "You can only move photos to your own entries"
            )
        return value

    def to_representation(self, instance):
        """Return detailed representation after update."""
        return PhotoDetailSerializer(instance, context=self.context).data
