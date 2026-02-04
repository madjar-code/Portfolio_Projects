# Error Handling and Logging

## Overview

The error handling and logging system in Photos API provides:
- Unified error response format
- Centralized exception handling
- Systematic logging of all operations
- Detailed information for debugging

---

## Custom Exception Handler

### Location
`apps/common/exceptions/handler.py`

### Functionality

Custom exception handler processes:
1. **Standard DRF exceptions** (ValidationError, NotFound, PermissionDenied)
2. **Custom application exceptions** (EntryNotFoundError, PhotoNotFoundError, etc.)
3. **Unexpected exceptions** (returns 500 Internal Server Error)

### Response Format

All errors are returned in a unified format:

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

### Handler Logging

- **ERROR level** - for all DRF exceptions and custom PhotosError
- **WARNING level** - for NotFound exceptions (EntryNotFoundError, PhotoNotFoundError)
- **CRITICAL level** - for unexpected exceptions

Each log entry contains:
- View class name
- User ID (or "Anonymous")
- HTTP method and path
- Full traceback (exc_info=True)

---

## Custom Exceptions

### Location
`apps/photos/exceptions.py`

### Exception Hierarchy

```
PhotosError (base class)
├── EntryNotFoundError
├── PhotoNotFoundError
├── MaxPhotosExceededError
├── InvalidPhotoFormatError
└── PhotoSizeTooLargeError
```

### Usage

**In serializers:**
```python
if value.size > max_size_mb * 1024 * 1024:
    raise PhotoSizeTooLargeError(f"Photo exceeds {max_size_mb}MB limit")

if ext not in allowed_formats:
    raise InvalidPhotoFormatError(f"Format {ext} not allowed")
```

**In views:**
```python
except Entry.DoesNotExist:
    logger.warning(f"User {self.request.user.id} tried to access entry {entry_id}")
    raise EntryNotFoundError("Entry not found")
```

---

## Logging Strategy

### Logger Configuration

Each view module has its own logger:
```python
import logging
logger = logging.getLogger(__name__)
```

### Logging Levels

**INFO** - Successful operations:
- List requests
- Resource creation
- Resource updates
- Resource deletion

**WARNING** - Expected errors:
- Attempt to access non-existent resource
- Attempt to access another user's resource

**ERROR** - Unexpected errors:
- Validation errors
- Business logic errors

**CRITICAL** - Critical errors:
- Unhandled exceptions
- System errors

### Logging Patterns

**List operations:**
```python
logger.info(f"User {request.user.id} requesting entry list")
# ... operation ...
logger.info(f"User {request.user.id} retrieved {len(entries)} entries")
```

**Create operations:**
```python
logger.info(f"User {request.user.id} creating new entry")
# ... operation ...
logger.info(f"User {request.user.id} created entry {entry.id}")
```

**Update operations:**
```python
logger.info(f"User {request.user.id} updating entry {entry_id}")
# ... operation ...
logger.info(f"User {request.user.id} updated entry {entry_id}")
```

**Delete operations:**
```python
logger.info(f"User {request.user.id} deleting entry {entry_id}")
# ... operation ...
logger.info(f"User {request.user.id} deleted entry {entry_id} with {photo_count} photos")
```

**Error scenarios:**
```python
logger.warning(f"User {self.request.user.id} tried to access non-existent entry {entry_id}")
```

---

## Error Scenarios by Endpoint

### Entry Endpoints

#### 1. GET /api/photos/entries/ - List Entries

**Success:**
- Status: 200 OK
- Logging: `INFO: User {id} requesting entry list` → `INFO: User {id} retrieved {count} entries`

**Errors:**
- **401 Unauthorized** - No authentication token
  - Code: `not_authenticated`
  - Logging: Handled by DRF middleware

---

#### 2. POST /api/photos/entries/create/ - Create Entry

**Success:**
- Status: 201 Created
- Logging: `INFO: User {id} creating new entry` → `INFO: User {id} created entry {entry_id}`

**Errors:**
- **401 Unauthorized** - No authentication token
  - Code: `not_authenticated`
- **400 Bad Request** - Missing title
  - Code: `validation_error`
  - Logging: `ERROR: API Error in EntryCreateView: ValidationError`
  - Response:
    ```json
    {
      "error": {
        "message": "This field is required.",
        "code": "validation_error",
        "status": 400,
        "details": {"title": ["This field is required."]}
      }
    }
    ```
- **400 Bad Request** - Title too long (>255 chars)
  - Code: `validation_error`
  - Logging: `ERROR: API Error in EntryCreateView: ValidationError`

---

#### 3. GET /api/photos/entries/{id}/ - Get Entry Details

**Success:**
- Status: 200 OK
- Logging: `INFO: User {id} requesting entry {entry_id}`

**Errors:**
- **401 Unauthorized** - No authentication token
- **404 Not Found** - Entry doesn't exist
  - Code: `entry_not_found`
  - Logging: `WARNING: User {id} tried to access non-existent entry {entry_id}`
  - Response:
    ```json
    {
      "error": {
        "message": "Entry not found",
        "code": "entry_not_found",
        "status": 404,
        "details": {}
      }
    }
    ```
- **403 Forbidden** - Entry belongs to another user
  - Code: `permission_denied`
  - Logging: `ERROR: API Error in EntryDetailView: PermissionDenied`

---

#### 4. PATCH /api/photos/entries/{id}/update/ - Update Entry

**Success:**
- Status: 200 OK
- Logging: `INFO: User {id} updating entry {entry_id}` → `INFO: User {id} updated entry {entry_id}`

**Errors:**
- **401 Unauthorized** - No authentication token
- **404 Not Found** - Entry doesn't exist
  - Logging: `WARNING: User {id} tried to update non-existent entry {entry_id}`
- **403 Forbidden** - Entry belongs to another user
- **400 Bad Request** - Invalid data

---

#### 5. DELETE /api/photos/entries/{id}/delete/ - Delete Entry

**Success:**
- Status: 204 No Content
- Logging: `INFO: User {id} deleting entry {entry_id}` → `INFO: User {id} deleted entry {entry_id} with {count} photos`

**Errors:**
- **401 Unauthorized** - No authentication token
- **404 Not Found** - Entry doesn't exist
  - Logging: `WARNING: User {id} tried to delete non-existent entry {entry_id}`
- **403 Forbidden** - Entry belongs to another user

---

### Photo Endpoints

#### 6. GET /api/photos/photos/ - List Photos

**Success:**
- Status: 200 OK
- Logging: `INFO: User {id} requesting photo list` → `INFO: User {id} retrieved {count} photos`

**Errors:**
- **401 Unauthorized** - No authentication token

---

#### 7. POST /api/photos/entries/{entry_id}/photos/create/ - Create Photo

**Success:**
- Status: 201 Created
- Logging: `INFO: User {id} creating new photo for entry {entry_id}` → `INFO: User {id} created photo {photo_id} in entry {entry_id}`

**Request:**
- Content-Type: `multipart/form-data`
- Path parameter: `entry_id` (UUID)
- Body: `file` (image file)

**Errors:**
- **401 Unauthorized** - No authentication token
- **400 Bad Request** - Missing required fields
  - Code: `validation_error`
  - Logging: `ERROR: API Error in PhotoCreateView: ValidationError`
- **400 Bad Request** - Entry doesn't belong to user
  - Code: `validation_error`
  - Logging: `ERROR: API Error in PhotoCreateView: ValidationError`
  - Response:
    ```json
    {
      "error": {
        "message": "Entry does not belong to you",
        "code": "validation_error",
        "status": 400,
        "details": {"entry": ["Entry does not belong to you"]}
      }
    }
    ```
- **400 Bad Request** - Max photos exceeded
  - Code: `max_photos_exceeded`
  - Logging: `WARNING: Max photos exceeded - User {id} in PhotoCreateView`
  - Response:
    ```json
    {
      "error": {
        "message": "Entry already has maximum 50 photos",
        "code": "max_photos_exceeded",
        "status": 400,
        "details": {}
      }
    }
    ```
- **400 Bad Request** - Photo size too large
  - Code: `photo_size_too_large`
  - Logging: `WARNING: Photo size too large - User {id} in PhotoCreateView`
  - Response:
    ```json
    {
      "error": {
        "message": "Photo exceeds 10MB limit",
        "code": "photo_size_too_large",
        "status": 400,
        "details": {}
      }
    }
    ```
- **400 Bad Request** - Invalid photo format
  - Code: `invalid_photo_format`
  - Logging: `WARNING: Invalid photo format - User {id} in PhotoCreateView`
  - Response:
    ```json
    {
      "error": {
        "message": "Format gif not allowed. Allowed: jpg, jpeg, png, webp",
        "code": "invalid_photo_format",
        "status": 400,
        "details": {}
      }
    }
    ```

---

#### 8. GET /api/photos/photos/{id}/ - Get Photo Details

**Success:**
- Status: 200 OK
- Logging: `INFO: User {id} requesting photo {photo_id}`

**Errors:**
- **401 Unauthorized** - No authentication token
- **404 Not Found** - Photo doesn't exist
  - Code: `photo_not_found`
  - Logging: `WARNING: User {id} tried to access non-existent photo {photo_id}`
- **403 Forbidden** - Photo belongs to another user

---

#### 9. PATCH /api/photos/photos/{id}/update/ - Update Photo

**Success:**
- Status: 200 OK
- Logging: `INFO: User {id} updating photo {photo_id}` → `INFO: User {id} updated photo {photo_id}`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (new image file)

**Errors:**
- **401 Unauthorized** - No authentication token
- **404 Not Found** - Photo doesn't exist
  - Logging: `WARNING: User {id} tried to update non-existent photo {photo_id}`
- **403 Forbidden** - Photo belongs to another user
- **400 Bad Request** - Photo size too large
- **400 Bad Request** - Invalid photo format
- **400 Bad Request** - Missing file field

---

#### 10. DELETE /api/photos/photos/{id}/delete/ - Delete Photo

**Success:**
- Status: 204 No Content
- Logging: `INFO: User {id} deleting photo {photo_id}` → `INFO: User {id} deleted photo {photo_id} from entry {entry_id}`

**Errors:**
- **401 Unauthorized** - No authentication token
- **404 Not Found** - Photo doesn't exist
  - Logging: `WARNING: User {id} tried to delete non-existent photo {photo_id}`
- **403 Forbidden** - Photo belongs to another user

---

## Error Codes Reference

| Code | HTTP Status | Description | Logging Level |
|------|-------------|-------------|---------------|
| `not_authenticated` | 401 | Missing or invalid authentication | INFO (middleware) |
| `permission_denied` | 403 | User doesn't have permission | ERROR |
| `validation_error` | 400 | Invalid input data | ERROR |
| `entry_not_found` | 404 | Entry doesn't exist | WARNING |
| `photo_not_found` | 404 | Photo doesn't exist | WARNING |
| `max_photos_exceeded` | 400 | Entry has reached photo limit | WARNING |
| `photo_size_too_large` | 400 | Photo file exceeds size limit | WARNING |
| `invalid_photo_format` | 400 | Photo format not allowed | WARNING |
| `internal_error` | 500 | Unexpected server error | CRITICAL |

---

## Configuration

### Settings (base.py)
```python
REST_FRAMEWORK = {
    ...
    "EXCEPTION_HANDLER": "apps.common.exceptions.handler.custom_exception_handler",
}
```

### Logging (dev.py)
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

### Photo Settings
```python
MAX_PHOTOS_PER_ENTRY = 50
MAX_PHOTO_SIZE_MB = 10
ALLOWED_PHOTO_FORMATS = "jpg,jpeg,png,webp"
```

---

## Best Practices

1. **Always log operation start and end** for performance tracking
2. **Use WARNING for expected errors** (NotFound, PermissionDenied)
3. **Use ERROR for unexpected errors** (ValidationError, business logic)
4. **Include context in logs** (user_id, resource_id, operation)
5. **Use custom exceptions** instead of generic ValidationError where possible
6. **Unified response format** for all errors
7. **Detailed information in details** for frontend debugging

