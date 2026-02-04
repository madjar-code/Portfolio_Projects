class PhotosError(Exception):
    """Base exception for photos app."""
    pass


class EntryNotFoundError(PhotosError):
    """Raised when entry is not found."""
    pass


class PhotoNotFoundError(PhotosError):
    """Raised when photo is not found."""
    pass


class MaxPhotosExceededError(PhotosError):
    """Raised when max photos per entry limit is exceeded."""
    pass


class InvalidPhotoFormatError(PhotosError):
    """Raised when photo format is not allowed."""
    pass


class PhotoSizeTooLargeError(PhotosError):
    """Raised when photo size exceeds limit."""
    pass
