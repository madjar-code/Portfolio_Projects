# N-tier Monolith Architecture

[Initial Notes](https://www.notion.so/Initial-Notes-2d83ba5e2c158064bfb9e113f95e1df8?pvs=21)

# Personal Gallery: Pragmatic Django DRF Architecture

## Overview

This document outlines the layered architecture for the **Personal Gallery** backend API. The system is built with **Django REST Framework** and follows a pragmatic approach that balances clean architecture principles with Django's MVT model, avoiding unnecessary complexity while maintaining clear separation of concerns.

### Key Architectural Principles

1. **No Repository Pattern** — Django's ORM QuerySets and Managers are sufficient; an additional repository layer adds unnecessary abstraction
2. **Service Layer for Business Logic** — Complex business rules are isolated in services, not scattered in serializers or models
3. **Pragmatic, Not Pure** — We follow SOLID principles but avoid over-engineering typical to monolithic Django applications
4. **Infrastructure Adapters** — External service integrations (S3, Redis, Celery, SMTP, OAuth) are encapsulated in adapter classes
5. **Clear Data Flow** — Request → Views→ Serializer → Service → Models → Adapters → External Services

---

## Layered Architecture

### Layer 1: API Layer (Presentation)

**Responsibility:** HTTP request handling, routing, thin controllers

**Location:** **`gallery/api/views.py`**

- Only serialization/deserialization
- Permission checking
- Direct delegation to service layer
- **NO business logic**

### Layer 2: Serializers Layer (Input/Output Validation & Transformation)

**Responsibility:** Data validation, serialization, deserialization

**Location:** **`gallery/api/serializers.py`**

- Validate input data (size, format, type constraints)
- Validate required fields
- Transform data types if needed
- Serialize models to JSON for responses
- **NO business logic** (that's the service's job)

### Layer 3: Service Layer (Business Logic)

**Responsibility:** Complex business rules, orchestration, transactions

**Location:** **`gallery/services/photo_service.py`**, **`entry_service.py`**, etc.

- Implement business rules (limits, status checks, policies)
- Coordinate between models and adapters
- Handle transactions
- Validate business constraints
- Reusable across API, commands, tasks, other services

### Layer 4: Models & Managers (Data Persistence)

**Responsibility:** Data persistence, simple queries, domain entities

**Location:** **`gallery/models/photo.py`**, **`entry.py`**

- Define database schema
- Custom managers for complex querysets
- **NO methods** — keep models simple
- Database indexes for performance

### Layer 5: Adapters (Infrastructure & External Services)

**Responsibility:** Encapsulate external system interactions

**Location:** **`gallery/adapters/storage.py`**, **`cache.py`**, **`tasks.py`**

- S3/MinIO upload/download
- Redis caching
- Celery task scheduling
- SMTP email sending
- Google OAuth verification

---

## **Complete Request Flow: Photo Upload**

```markdown
1. HTTP POST /api/gallery/photos/
   ↓
2. PhotoViewSet.create(request)
   - Extract request.data
   - Call serializer
   ↓
3. PhotoCreateSerializer.is_valid()
   - Validate file size (max 10MB)
   - Validate MIME type (JPEG/PNG only)
   - Validate title/description length
   - Return validated_data or raise ValidationError
   ↓
4. PhotoService.create_photo(user, file, metadata)
   ├─ BUSINESS LOGIC CHECKS:
   │  ├─ Is user active?
   │  ├─ Has user hit photo limit (1000)?
   │  ├─ Do we have available quota?
   │  └─ Is file format allowed? (redundant, but final check)
   │
   ├─ DATABASE TRANSACTION:
   │  └─ Photo.objects.create(user=user, title=title, ...)
   │     → Returns photo instance with id
   │
   ├─ EXTERNAL SERVICE CALLS (Adapters):
   │  ├─ StorageAdapter.upload_photo(photo_id, file)
   │  │  → Returns S3 URL
   │  │  → Update photo.file_url
   │  │
   │  └─ CacheAdapter.invalidate_user_photos_cache(user_id)
   │     → Clear Redis cache
   │
   └─ Return updated photo instance
   ↓
5. PhotoSerializer(photo)
   - Transform model → JSON response
   - Include file_url, created_at, etc.
   ↓
6. Response (201 Created + JSON)

```

---

## Project Structure

That’s an approximate structure of the project that contains only one application for the gallery functionality.

```markdown
personal_gallery/
├── apps/
│   └── gallery/
│       ├── api/
│       │   ├── views.py
│       │   ├── serializers.py
│       │   └── urls.py
│       │
│       ├── services/
│       │   ├── photo_service.py
│       │   ├── entry_service.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── photo.py
│       │   └── entry.py
│       │
│       ├── adapters/
│       │   ├── storage.py
│       │   ├── cache.py
│       │   └── tasks.py
│       │
│       ├── migrations/
|       ├── exceptions.py
│       ├── admin.py
│       ├── apps.py
│       └── __init__.py
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── __init__.py
│
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── .env.example
```