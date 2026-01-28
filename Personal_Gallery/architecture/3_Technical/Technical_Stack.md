This section describes the technology stack of the *Personal Gallery* project and which technologies are used at each level of the system. The goal of the stack is to provide a realistic production‑like configuration without unnecessary complexity.

### Overview

The platform is a web application for a personal photo gallery with authentication, photo uploads, and basic statistics. The architecture is: **React SPA + Django API + PostgreSQL + S3‑compatible storage**, all deployed in Docker behind Nginx.

Main goals of the stack choice:

- Practice in system design (requirements specification, diagrams, data models).
- Practice with production‑like infrastructure (Docker, Nginx, object storage, DB backups).
- Ability to experiment with indexes, caching, and background tasks.

### Backend

**Language and framework**

- Python 3.11+
- Django (as the main web framework)
- Django REST Framework (for building JSON APIs)

**Reasons for choosing**

- Familiar stack, fast to start with.
- Out of the box: ORM, authentication, admin panel, migrations.
- Convenient for practicing layered architecture (models → repositories/services → API).

### Frontend

- React (Vite or Create React App as the build tool)
- TypeScript (optional, if you want practice with typing)
- Communication with the backend via REST API (JSON)

**Reasons for choosing**

- Separation of concerns: the frontend acts as an independent client to the API.
- Option to add other clients later (mobile app, SPA 2.0, etc.).

### Database Layer

- PostgreSQL

**Usage**

- Storing users, entries (Entry), photos (Photo), and auxiliary entities.
- Focus on:
  - normalized schema;
  - using indexes (by user, date, status, etc.);
  - practice in writing migrations and query optimization.

### Object & Static Storage

- S3‑compatible object storage (for example, **DigitalOcean Spaces**, MinIO locally)
- Django storage backend to work with the object storage
- Static files for the frontend and Django — either through the same storage, or via Nginx + filesystem

**Usage**

- Storing user photos.
- Storing derived files (for example, resized previews), if/when they appear.

### Caching & Background Tasks

- **Redis** (optional but desirable):
  - Caching aggregated statistics (number of entries, photos, etc.).
  - Potentially — a broker for background tasks (Celery/RQ), if we want to practice background processing (e.g., generating previews, periodic stats recalculation).

### Web Server & Deployment

- **Nginx**
  - Acts as a reverse proxy in front of Django (gunicorn).
  - Serves static files.
  - Terminates HTTPS.
- **Docker + docker-compose**
  - Separate services: **`web`** (Django), **`db`** (Postgres), **`redis`**, **`nginx`**, **`storage`** (MinIO locally).
  - Convenient to run both locally and on a VPS.

The goal is to practice a typical chain: Nginx → Django (gunicorn) → Postgres/Redis/S3.

### Authentication & External Services

- **Google OAuth** for user login.
- **Email/Password authentication** with account confirmation and password reset.
- Email service (SMTP/transactional service) for sending confirmation and password reset emails.

### Operations & Maintenance

- Periodic PostgreSQL database backups:
  - scripts/cron‑job or a separate container running **`pg_dump`** to the object storage.
- Logs and minimal monitoring:
  - logging Django to stdout (under Docker);
  - ability to add Sentry/Prometheus in the future.

### Design & Documentation Tooling

Although they are not part of the runtime stack, they are important for learning purposes:

- Excalidraw / draw.io / Mermaid — for:
  - Use Case diagrams;
  - Class / Domain Model diagrams;
  - Database ERD;
  - Sequence diagrams and system‑level diagrams.
- Notion — as the main storage for descriptions, requirements, and architecture.
