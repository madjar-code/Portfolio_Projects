# Backend API — Setup Spec

**Source documents:**
- [Backend API Architecture](../../2_Architecture/Architectural_Decisions/Backend_API_Architecture.md)
- [Technology Stack](../Technology_Stack.md)
- [Data Model](../../2_Architecture/Architectural_Decisions/Data_Model.md)
- [C4 Component Diagram](../../2_Architecture/Mermaid_Diagrams/c4-component-backend-api.md)

---

## 1. Overview

This spec defines the initial setup of the Backend API — the Django-based orchestrator of the Bureaucratic AI Agent system.

**Scope:** project initialization, directory structure, dependency configuration, settings split (base/dev/prod), Django apps registration, custom User model, common abstractions, database connection, MinIO storage integration.

**Out of scope:** endpoint implementation, business logic, Celery/RabbitMQ setup (deferred), migrations beyond the initial `migrate`.

---

## 2. Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.12+ |
| UV (package manager) | latest |
| Docker & Docker Compose | latest |
| PostgreSQL (via Docker) | 16 |
| MinIO (via Docker) | latest |

Local services are started via `docker compose up` from `backend/`.

---

## 3. Project Layout

```
backend/
├── manage.py
├── pyproject.toml              # dependencies, tool config
├── docker-compose.yml          # local dev services
├── .env                        # local env vars (not committed)
├── .env.example                # template for environment variables
│
├── config/                     # Django project package
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py                 # root URL configuration
│   └── settings/
│       ├── __init__.py
│       ├── base.py             # shared settings
│       ├── dev.py              # development overrides
│       └── prod.py             # production overrides
│
├── apps/                       # domain applications
│   ├── __init__.py
│   └── auth/                   # user authentication
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py           # User model
│       ├── managers.py
│       └── migrations/
│
├── common/                     # shared abstractions
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py               # BaseModel, UUIDModel, TimeStampModel, SoftDeletionModel, SlugModel
│   ├── managers.py             # SoftDeletionManager
│   ├── admin.py                # BaseAdmin, ReadOnlyFieldsAdmin, SoftDeletionAdmin
│   └── pagination.py           # StandardPagination
│
└── tests/
    ├── __init__.py
    └── auth/
```

---

## 4. Dependencies

### Core

| Package | Version | Purpose |
|---|---|---|
| `django` | ^6.0 | Web framework |
| `django-jazzmin` | ^3.0 | Admin UI theme |
| `djangorestframework` | ^3.17 | REST API |
| `psycopg[binary]` | ^3.3 | PostgreSQL adapter |
| `django-storages` | ^1.14 | S3/MinIO storage backend |
| `boto3` | ^1.42 | AWS S3 SDK |
| `djangorestframework-simplejwt` | ^5.5 | JWT authentication |
| `pillow` | ^11.0 | Image processing (avatar upload) |
| `python-dotenv` | ^1.2 | Environment variable loading |
| `gunicorn` | ^25.0 | WSGI server |

---

## 5. Configuration

### 5.1 Settings modules

`DJANGO_SETTINGS_MODULE` controls which settings file is loaded:

| Value | Used when |
|---|---|
| `config.settings.dev` | Local development |
| `config.settings.prod` | Production / CI |

`dev.py` and `prod.py` import everything from `base.py` and override only what differs.

`dev.py` overrides: `DEBUG = True`, `AWS_S3_USE_SSL = False`.

### 5.2 Environment variables

Loaded from `.env` via `python-dotenv`. `.env.example` must be kept up to date. `SECRET_KEY` must not contain `$` characters (Docker Compose interpolation conflict).

| Variable | Required | Example | Description |
|---|---|---|---|
| `SECRET_KEY` | yes | `django-insecure-...` | Django secret key (no `$` chars) |
| `DEBUG` | yes | `True` | Debug mode |
| `ALLOWED_HOSTS` | yes | `localhost,127.0.0.1` | Comma-separated hosts |
| `DB_NAME` | yes | `django_db` | PostgreSQL database name |
| `DB_USER` | yes | `django_user` | PostgreSQL user |
| `DB_PASSWORD` | yes | `django_pass` | PostgreSQL password |
| `DB_HOST` | yes | `localhost` | PostgreSQL host |
| `DB_PORT` | yes | `5433` | PostgreSQL port (5433 to avoid local PG conflict) |
| `AWS_ACCESS_KEY_ID` | yes | `minioadmin` | MinIO access key |
| `AWS_SECRET_ACCESS_KEY` | yes | `minioadmin` | MinIO secret key |
| `AWS_STORAGE_BUCKET_NAME` | yes | `bureaucratic-docs` | Bucket name |
| `AWS_S3_ENDPOINT_URL` | yes | `http://localhost:9000` | MinIO endpoint |
| `AGENT_API_KEY` | yes | `secret-key-123` | Key for AI agent callback authentication |

### 5.3 `base.py` defines

- `INSTALLED_APPS`: `jazzmin`, Django defaults, `rest_framework`, `rest_framework_simplejwt`, `storages`, `common`, `apps.auth`
- `AUTH_USER_MODEL = "auth_app.User"`
- `REST_FRAMEWORK`: JWT authentication, `IsAuthenticated` permission
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`
- `STORAGES`: S3Boto3Storage as default backend
- `AWS_S3_ADDRESSING_STYLE = "path"` — required for MinIO path-style URLs
- `AWS_QUERYSTRING_AUTH = False` — public direct URLs
- `MEDIA_URL` — built from endpoint + bucket name

---

## 6. Django Apps

| App | Django label | Purpose |
|---|---|---|
| `common` | `common` | Shared abstract models, managers, admin base classes, pagination |
| `apps.auth` | `auth_app` | Custom User model |

> `apps.auth` uses label `auth_app` to avoid conflict with Django's built-in `django.contrib.auth`.

### common — abstract models

| Class | Purpose |
|---|---|
| `UUIDModel` | UUID primary key |
| `TimeStampModel` | `created_at`, `updated_at` |
| `SoftDeletionModel` | `is_active`, `soft_delete()`, `restore()` |
| `SlugModel` | Random URL-safe slug generation |
| `BaseModel` | Combines UUID + Timestamp + SoftDeletion |

### Custom User model

`apps.auth.models.User` extends `UUIDModel`, `TimeStampModel`, `AbstractBaseUser`, `PermissionsMixin`.

| Field | Type | Notes |
|---|---|---|
| `email` | EmailField | unique, `USERNAME_FIELD` |
| `full_name` | CharField | required |
| `phone` | CharField | optional |
| `avatar` | ImageField | optional, stored in MinIO under `avatars/` |
| `is_active` | BooleanField | soft delete flag |
| `is_staff` | BooleanField | admin access |
| `is_verified` | BooleanField | email verification |
| `last_login_at` | DateTimeField | optional |

---

## 7. Docker Compose (dev)

Located at `backend/docker-compose.yml`. Uses `env_file: .env`.

| Service | Image | Exposed port |
|---|---|---|
| `db` | `postgres:16` | `5433:5432` |
| `minio` | `minio/minio` | `9000` (API), `9001` (console) |

MinIO bucket `bureaucratic-docs` must be created manually with **public** access policy.

---

## 8. Verification

```bash
# 1. Django system check
uv run python manage.py check
# Expected: "System check identified no issues"

# 2. Migrations
uv run python manage.py makemigrations
uv run python manage.py migrate
# Expected: all migrations applied

# 3. Development server starts
uv run python manage.py runserver
# Expected: server running at http://127.0.0.1:8000/

# 4. MinIO storage connection
uv run python -c "
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev'
django.setup()
from django.core.files.storage import default_storage
print(default_storage.bucket_name)
"
# Expected: bureaucratic-docs
```
