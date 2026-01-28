# Personal (Remote) Gallery: Code Style Guide

## General Principles

- Follow PEP 8 as the base Python style guide
- Prioritize code readability and maintainability
- Use consistent naming conventions throughout the project
- Write self-documenting code with meaningful names
- Aim for clarity over cleverness

---

## String Formatting

### Rules

- **Use double quotes `"` instead of single quotes `'`** for all strings
- Use f-strings for string interpolation when possible
- Use triple double quotes `"""` for docstrings and multi-line strings

### Examples

```python
# Good
name = "John Doe"
message = f"Hello, {name}!"
description = """
This is a multi-line
docstring example.
"""

# Bad
name = 'John Doe'
message = "Hello, " + name + "!"

```

---

## Import Organization

### Import Order (following isort configuration)

1. **Standard library imports**
2. **Third-party library imports**
3. **Local application imports**

Each group should be separated by a blank line, and imports within each group should be alphabetically sorted.

### Formatting Rules

- Use absolute imports whenever possible
- Avoid wildcard imports (`from module import *`)
- Keep imports on single lines when possible
- For long imports, use parentheses for line continuation
- Maximum line length: 88 characters (Black default)

### Examples

```python
# Standard library imports
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

# Third-party imports
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.urls import path
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Local application imports
from gallery.exceptions import EntryNotFoundError, PhotoNotFoundError
from gallery.models import Entry, Photo, User
from gallery.repositories import EntryRepository, PhotoRepository
from gallery.schemas import EntrySerializer, PhotoSerializer
from gallery.services import EntryService, PhotoService

```

### Single-Line vs Multi-Line Imports

```python
# Good - single line
from gallery.repositories import EntryRepository

# Good - multiple imports from same module
from gallery.models import (
    Entry,
    Photo,
    User
)

# Good - long import with line break
from gallery.services.very_long_module_name import (
    VeryLongServiceClassName
)

```

---

## Naming Conventions

### Variables and Functions

- Use `snake_case` for variables, functions, and module names
- Use descriptive names that explain the purpose
- Avoid single-letter variables except in loops (i, j) or mathematical contexts

```python
# Good
entry_id = "123e4567-e89b-12d3-a456-426614174000"
user_email = "user@example.com"
max_photos_per_entry = 50

def get_entry_by_id(entry_id: UUID) -> Optional[Entry]:
    pass

def upload_photo(file, entry_id: UUID) -> Photo:
    pass

# Bad
eid = "123e4567-e89b-12d3-a456-426614174000"
e = "user@example.com"
max_ph = 50

def getEntry(id):
    pass

```

### Classes

- Use `PascalCase` for class names
- Use descriptive nouns that represent the entity or concept
- Suffix repository classes with `Repository`
- Suffix service classes with `Service`
- Suffix exception classes with `Error`

```python
# Good
class Entry(models.Model):
    pass

class EntryRepository:
    pass

class EntryService:
    pass

class EntryNotFoundError(Exception):
    pass

# Bad
class entry:
    pass

class EntryRepo:
    pass

class EntryLogic:
    pass

```

### Constants

- Use `UPPER_SNAKE_CASE` for constants
- Define constants at module level
- Group related constants together

```python
# Good
DEFAULT_PAGE_SIZE = 20
MAX_PHOTOS_PER_ENTRY = 50
MAX_PHOTO_SIZE_MB = 10
ALLOWED_PHOTO_FORMATS = ("jpg", "jpeg", "png", "webp")

# Bad
default_page_size = 20
MaxPhotosPerEntry = 50
max_photo_mb = 10

```

---

## File and Directory Structure

### File Naming

- Use `snake_case` for Python file names
- Use descriptive names that indicate the file's purpose
- Match module names with their primary class (e.g., `entry_service.py` contains `EntryService`)

```
# Good
entry.py
entry_repository.py
entry_service.py
photo_uploader.py

# Bad
Entry.py
EntryRepo.py
service.py
uploader_util.py

```

### Directory Structure

Follow the layered architecture pattern with two Django applications:

```
auth/                 # Authentication and user management
├── api/
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── models/
├── services/
├── repositories/
├── exceptions/
├── utils/
├── migrations/
└── tests/

photos/               # Entry and Photo entities
├── api/
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── models/
├── services/
├── repositories/
├── exceptions/
├── utils/
├── migrations/
└── tests/

```

---

## Code Formatting

### Line Length

- **Maximum line length: 88 characters** (Black default)
- Break long lines using parentheses or line continuation

### Indentation

- Use **4 spaces** for indentation (no tabs)
- Align continuation lines properly

### Examples

```python
# Good - function definition
def create_entry(
    title: str,
    description: str,
    user: User,
    photos: List[Photo]
) -> Entry:
    return Entry(
        title=title,
        description=description,
        user=user,
        photos=photos
    )

# Good - long if statement
if (
    entry.user == current_user
    and entry.created_at > datetime.now() - timedelta(hours=1)
):
    return Response({"message": "Can edit this entry"})

# Good - dictionary with many items
photo_metadata = {
    "filename": filename,
    "size": size_mb,
    "format": format_type,
    "upload_timestamp": datetime.now().isoformat()
}

```

### Blank Lines

- Two blank lines between top-level classes and functions
- One blank line between methods within a class
- Use blank lines sparingly within functions to separate logical sections

```python
class EntryService:
    """Service for managing entries."""

    def __init__(self, repository: EntryRepository) -> None:
        """Initialize the service."""
        self._repository = repository

    def get_entry(self, entry_id: UUID) -> Optional[Entry]:
        """Retrieve entry by ID."""
        return self._repository.get_by_id(entry_id)

    def create_entry(self, data: dict) -> Entry:
        """Create a new entry."""
        return self._repository.create(data)

```

---

## Type Hints

### Required Usage

- **Always use type hints** for function parameters and return values
- Use type hints for class attributes when not obvious
- Import types from `typing` module when needed

### Examples

```python
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

def get_entries(
    user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Entry]:
    pass

def find_entry_by_id(entry_id: UUID) -> Optional[Entry]:
    pass

class EntryService:
    def __init__(self, repository: EntryRepository) -> None:
        self._repository = repository
        self._cache: Dict[UUID, Entry] = {}

    def get_user_entries(self, user_id: UUID) -> List[Entry]:
        pass

```

### Optional Types

- Use `Optional[Type]` for nullable values
- Use `Union[Type1, Type2]` for multiple possible types
- Use `Type | None` for Python 3.10+

```python
# Good
def find_by_id(entry_id: UUID) -> Optional[Entry]:
    pass

# Also acceptable (Python 3.10+)
def find_by_id(entry_id: UUID) -> Entry | None:
    pass

# Union type
from typing import Union

def process_media(data: Union[str, bytes]) -> None:
    pass

```

---

## Documentation

### Docstrings

- Use triple double quotes `"""` for all docstrings
- Follow Google docstring style
- Include parameter descriptions, return value information, and exceptions

### Examples

```python
def get_entry_by_id(entry_id: UUID) -> Optional[Entry]:
    """
    Retrieve an entry by its unique identifier.

    Args:
        entry_id: The unique identifier of the entry.

    Returns:
        The Entry object if found, None otherwise.

    Raises:
        EntryNotFoundError: If the entry doesn't exist in the repository.
    """
    try:
        return Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        raise EntryNotFoundError(f"Entry {entry_id} not found")

class EntryService:
    """
    Service layer for managing entries and their operations.

    Handles creation, retrieval, updating, and deletion of entries,
    as well as photo management and caching.
    """

    def __init__(self, repository: EntryRepository) -> None:
        """
        Initialize the EntryService.

        Args:
            repository: The repository instance for data access.
        """
        self._repository = repository

```

### Comments

- Use comments sparingly for complex business logic
- Avoid obvious comments
- Use `# TODO:` for temporary code that needs improvement

```python
# Good - explains non-obvious logic
# Calculate optimal compression ratio based on file size and format
compression_level = min(9, (file_size_mb * 0.5) // 100)

# Bad - obvious comment
# Set status to active
status = "active"

# TODO: Implement caching for frequently accessed entries
def get_popular_entries():
    pass

```

---

## Error Handling

### Exception Naming

- Use descriptive exception names ending with `Error`
- Inherit from appropriate base exception classes
- Include helpful error messages

```python
# gallery/exceptions.py

class GalleryError(Exception):
    """Base exception for gallery application."""
    pass

class EntryNotFoundError(GalleryError):
    """Raised when an entry cannot be found."""
    pass

class PhotoNotFoundError(GalleryError):
    """Raised when a photo cannot be found."""
    pass

class InvalidPhotoError(GalleryError):
    """Raised when photo data is invalid."""
    pass

class PhotoUploadError(GalleryError):
    """Raised when photo upload fails."""
    pass

class StorageError(GalleryError):
    """Raised when object storage operations fail."""
    pass

```

### Exception Handling

- Be specific about which exceptions you catch
- Always log exceptions appropriately
- Use custom exceptions for domain-specific errors

```python
# Good - specific exception handling
try:
    entry = Entry.objects.get(id=entry_id)
except Entry.DoesNotExist:
    logger.warning(f"Entry not found: {entry_id}")
    raise EntryNotFoundError(f"Entry {entry_id} not found")
except Exception as e:
    logger.error(f"Unexpected error retrieving entry: {e}")
    raise

# Bad - too broad
try:
    entry = Entry.objects.get(id=entry_id)
except Exception:
    pass

```

---

## Logging

### Logger Configuration

- Use module-level loggers
- Include meaningful context in log messages
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Examples

```python
import logging

logger = logging.getLogger(__name__)

def get_entry(entry_id: UUID) -> Entry:
    """Retrieve an entry by ID."""
    logger.debug(f"Retrieving entry: {entry_id}")
    try:
        entry = Entry.objects.get(id=entry_id)
        logger.info(f"Successfully retrieved entry: {entry_id}")
        return entry
    except Entry.DoesNotExist:
        logger.warning(f"Entry not found: {entry_id}")
        raise EntryNotFoundError(f"Entry {entry_id} not found")
    except Exception as e:
        logger.error(f"Error retrieving entry {entry_id}: {e}", exc_info=True)
        raise

def upload_photo(file, entry_id: UUID) -> Photo:
    """Upload a photo to an entry."""
    logger.info(f"Starting photo upload for entry: {entry_id}, file: {file.name}")
    try:
        photo = Photo.objects.create(file=file, entry_id=entry_id)
        logger.info(f"Photo uploaded successfully: {photo.id}")
        return photo
    except Exception as e:
        logger.error(f"Photo upload failed for entry {entry_id}: {e}", exc_info=True)
        raise PhotoUploadError(f"Failed to upload photo: {str(e)}")

```

---

## Tools and Automation

### Code Formatting

- **Black**: Automatic code formatting
- **isort**: Import sorting and organization
- Run before committing code

```bash
# Format code
black auth/ photos/
isort auth/ photos/

# Check formatting (useful in CI)
black --check auth/ photos/
isort --check-only auth/ photos/

```

### Type Checking

- **mypy**: Static type checking
- Configure in `pyproject.toml`

```bash
# Run type checking
mypy auth/ photos/

```

### Linting

- **flake8** or **ruff**: Code linting
- Configure to work with Black (line length 88)

```bash
# Run linting
flake8 auth/ photos/
# or
ruff check auth/ photos/

```

### Pre-commit Configuration

Use pre-commit hooks to ensure code quality before committing:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: <https://github.com/psf/black>
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: <https://github.com/pycqa/isort>
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: <https://github.com/pre-commit/mirrors-mypy>
    rev: v1.4.1
    hooks:
      - id: mypy
        additional_dependencies: [django-stubs]

  - repo: <https://github.com/pycqa/flake8>
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

```

---

## Project-Specific Guidelines

### UUID Usage

- Always use UUID4 for new identifiers
- Store UUIDs as strings in JSON responses
- Convert to UUID objects in Python code when needed

```python
from uuid import UUID, uuid4

# Model definition
class Entry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)

# In serializer
class EntrySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Entry
        fields = ["id", "title"]

```

### DateTime Handling

- Use ISO 8601 format for datetime strings in JSON
- Always use UTC timezone for storage
- Convert to local timezone only for display

```python
from datetime import datetime, timezone
import json

# Good
created_at = datetime.now(timezone.utc).isoformat()

# In Django models
class Entry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# In serializer
class EntrySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

```

### File Handling

- Use consistent indentation (2 spaces) in JSON files
- Handle file I/O errors gracefully
- Validate file formats and sizes before processing

```python
import os
from django.core.files.storage import default_storage

MAX_PHOTO_SIZE_MB = 10
ALLOWED_FORMATS = ("jpg", "jpeg", "png", "webp")

def validate_photo_file(file) -> bool:
    """Validate photo file before upload."""
    # Check size
    if file.size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        raise InvalidPhotoError(
            f"File size exceeds {MAX_PHOTO_SIZE_MB}MB limit"
        )

    # Check format
    ext = os.path.splitext(file.name)[1].lower().lstrip(".")
    if ext not in ALLOWED_FORMATS:
        raise InvalidPhotoError(
            f"Format {ext} not allowed. Allowed: {', '.join(ALLOWED_FORMATS)}"
        )

    return True

```

### Environment Variables

- Use lowercase with underscores for environment variable names
- Always have sensible defaults or raise clear errors

```python
# settings.py
import os
from pathlib import Path

DEBUG = os.getenv("DEBUG", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/personal_gallery"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("AWS credentials not configured")

```

---

## Summary Checklist

Before committing code, verify:

- [ ]  Code follows PEP 8
- [ ]  All strings use double quotes
- [ ]  Imports are organized and sorted
- [ ]  All functions and methods have type hints
- [ ]  Docstrings present for public functions/classes
- [ ]  Exception handling is specific
- [ ]  Logging is appropriate
- [ ]  Line length does not exceed 88 characters
- [ ]  Black and isort have been run
- [ ]  No `print()` statements (use logging instead)
- [ ]  No wildcard imports
- [ ]  No commented-out code (or marked with TODO)