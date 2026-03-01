# Error Handling and Logging

## Overview

The error handling and logging system provides:
- Unified error response format across all API endpoints
- Centralized exception handling
- Systematic logging of operations and errors
- Clear separation between expected and unexpected errors

---

## Custom Exception Handler

### Location
`apps/common/exceptions/handler.py`

### Functionality

The custom exception handler processes:
1. **Standard DRF exceptions** (ValidationError, NotFound, PermissionDenied)
2. **Custom application exceptions** (PhotosAPIException and subclasses)
3. **Unexpected exceptions** (returns 500 Internal Server Error)

### Response Format

All errors return a unified JSON structure:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "machine_readable_error_code",
    "status": 400,
    "details": {}
  }
}
```

### Logging Strategy

- **WARNING level** - for validation errors and expected business logic errors
- **ERROR level** - for permission denied and not found errors
- **CRITICAL level** - for unexpected system errors

Each log entry includes:
- View class name
- User identification
- HTTP method and path
- Full traceback for debugging (when applicable)

---

## Custom Exceptions

### Location
`apps/photos/exceptions.py`

### Exception Hierarchy

```
PhotosAPIException (base class, inherits from DRF's APIException)
├── MaxPhotosExceededError
├── InvalidPhotoFormatError
└── PhotoSizeTooLargeError
```

**Note:** `NotFound` errors (404) are handled automatically by DRF's generic views and don't require custom exceptions.

### Usage Examples

**In serializers:**
```python
if value.size > max_size_mb * 1024 * 1024:
    raise PhotoSizeTooLargeError(f"Photo exceeds {max_size_mb}MB limit")

if ext not in allowed_formats:
    raise InvalidPhotoFormatError(f"Format {ext} not allowed")

if photo_count >= max_photos:
    raise MaxPhotosExceededError(f"Entry already has {max_photos} photos")
```

---

## Logging Strategy

### Logger Configuration

Each module uses Python's standard logging:
```python
import logging
logger = logging.getLogger(__name__)
```

### Logging Levels

**INFO** - Successful operations and normal flow
**WARNING** - Expected errors (validation, business rules)
**ERROR** - Permission and access errors
**CRITICAL** - Unexpected system errors

### General Logging Patterns

Log important operations with context:
```python
# Successful operations
logger.info(f"User {user_id} performed {operation}")

# Expected errors
logger.warning(f"Validation failed: {error_details}")

# Unexpected errors
logger.error(f"Unexpected error in {view_name}", exc_info=True)
```

---

## API Endpoints Overview

### Entry Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/entries/` | List all entries | Optional |
| POST | `/api/entries/create/` | Create new entry | Required |
| GET | `/api/entries/<slug>/` | Get entry details | Optional |
| PATCH | `/api/entries/<slug>/update/` | Update entry | Required (Owner) |
| DELETE | `/api/entries/<slug>/delete/` | Delete entry (soft) | Required (Owner) |

### Photo Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/photos/` | List user's photos | Required |
| POST | `/api/photos/create/` | Upload photo | Required |
| GET | `/api/photos/<uuid>/` | Get photo details | Required (Owner) |
| PATCH | `/api/photos/<uuid>/update/` | Move photo to another entry | Required (Owner) |
| DELETE | `/api/photos/<uuid>/delete/` | Delete photo (soft) | Required (Owner) |

---

## Common Error Scenarios

### Authentication Errors
- **401 Unauthorized** - Missing or invalid authentication token
  - Code: `not_authenticated`
  - Returned by DRF middleware

### Permission Errors
- **403 Forbidden** - User doesn't own the resource
  - Code: `permission_denied`
  - Logged at ERROR level

### Validation Errors
- **400 Bad Request** - Invalid input data
  - Code: `validation_error`
  - Logged at WARNING level
  - Details field contains specific validation errors

### Not Found Errors
- **404 Not Found** - Resource doesn't exist
  - Code: `not_found`
  - Handled automatically by DRF generic views
  - Logged at ERROR level

### Photo-Specific Errors

**Max Photos Exceeded:**
```json
{
  "error": {
    "message": "Entry already has 50 photos. Maximum allowed is 50.",
    "code": "max_photos_exceeded",
    "status": 400
  }
}
```

**Photo Size Too Large:**
```json
{
  "error": {
    "message": "Photo size (12.5MB) exceeds maximum allowed size of 10MB",
    "code": "photo_size_too_large",
    "status": 400
  }
}
```

**Invalid Photo Format:**
```json
{
  "error": {
    "message": "Invalid photo format 'GIF'. Allowed formats: JPEG, PNG, WEBP",
    "code": "invalid_photo_format",
    "status": 400
  }
}
```

---

## Error Codes Reference

| Code | HTTP Status | Description | Logging Level |
|------|-------------|-------------|---------------|
| `not_authenticated` | 401 | Missing or invalid authentication | INFO |
| `permission_denied` | 403 | User doesn't have permission | ERROR |
| `validation_error` | 400 | Invalid input data | WARNING |
| `not_found` | 404 | Resource doesn't exist | ERROR |
| `max_photos_exceeded` | 400 | Entry has reached photo limit | WARNING |
| `photo_size_too_large` | 400 | Photo file exceeds size limit | WARNING |
| `invalid_photo_format` | 400 | Photo format not allowed | WARNING |
| `internal_error` | 500 | Unexpected server error | CRITICAL |

---

## Configuration

### Exception Handler (settings/base.py)
```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.common.exceptions.handler.custom_exception_handler",
    # ... other settings
}
```

### Logging Configuration (settings/dev.py)
```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
```

### Photo Validation Settings
```python
# Maximum photos per entry
MAX_PHOTOS_PER_ENTRY = 50

# Maximum file size in MB
MAX_PHOTO_SIZE_MB = 10

# Allowed image formats
ALLOWED_PHOTO_FORMATS = ["JPEG", "PNG", "WEBP"]
```

---

## Best Practices

1. **Use appropriate logging levels** - WARNING for expected errors, ERROR for unexpected
2. **Include context in logs** - user ID, resource ID, operation type
3. **Use custom exceptions** for domain-specific errors
4. **Maintain unified response format** across all endpoints
5. **Provide helpful error messages** for debugging and user feedback
6. **Log with exc_info=True** for unexpected errors to capture full traceback

