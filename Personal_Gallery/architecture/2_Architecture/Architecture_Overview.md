## 1. Architecture Overview

The *Personal Gallery* system is a web application for managing a personal photo gallery, including user registration, creating entries (Entry), uploading photos (Photo), simple moderation, and basic statistics. The application architecture follows the classic **client-server model** and includes a web client (SPA) and backend API.

Main technical decisions:

- Frontend — **React SPA**, interacting with the server via HTTP through **RESTful API** (GraphQL may be introduced later for query optimization).
- Backend — **Django + Django REST Framework**, implementing API and business logic within a layered architecture.
- The application will be implemented as a **monolithic backend service**, but with structuring by layers and modules to simplify maintenance and future scaling.
- Data storage:
    - main data source — **PostgreSQL**;
    - files and photos — **S3-compatible object storage** (DigitalOcean Spaces / MinIO).
- Infrastructure — **Docker + docker-compose**, deployment on VPS with Nginx (reverse proxy + static files + TLS).

The main architectural principle — **simplicity, extensibility, and realism for educational and practical purposes**.

---

## 2. Backend Layered Architecture

The backend is implemented following the **multi-tier architecture** principle, where each layer has clear responsibilities:

1. **API Layer**
    - Django REST Framework, primarily CBV / ViewSets
    - HTTP request handling, input data validation
    - returning serialized JSON responses
2. **Serialization Layer**
    - DRF serializers as a bridge between API and model layer
    - performing basic validation and data transformation
3. **Domain / ORM Layer**
    - Django models + business entity attributes
    - **repositories** (optional) for query encapsulation
4. **Service Layer**
    - business operations on domain logic
    - interaction with external services (email, object storage)
    - launching background tasks
5. **Infrastructure Layer**
    - caching (Redis)
    - Celery background tasks
    - integration adapters (OAuth, email provider)
6. **Persistence Layer**
    - PostgreSQL as transactional storage

This separation allows decoupling business logic from infrastructure and simplifies testing.

---

## 3. Design Patterns (Backend)

The architecture assumes the use of the following approaches and patterns:

- **Django MVC pattern** in the context of the web framework.
- **Repository (optional)**

    for isolating ORM queries and facilitating possible migration to other storage or services.

- **Ports & Adapters (Hexagonal elements)**

    for infrastructure integrations:

    - authentication (Google OAuth)
    - caching
    - background processing
    - email notifications
- **Custom Exceptions**
    - centralized error handling
    - unified error response structure

The goal — minimize code complexity while introducing clear architectural practices.

---

## 4. Application and Folder Structure (Backend)

The project is organized as a classic Django monolith with modular structure and domain context separation. Two applications are planned:

- `auth` — authentication and user management (OAuth, Email/Password, password recovery)
- `photos` — Entry / Photo / gallery entities

Basic template for each application structure:

```
app/
  api/
    serializers/
    views/
    urls.py
  models/
  services/
  repositories/
  exceptions/
  enums/
  utils/
```

Advantages:

- clear layer separation
- simplified maintenance
- possibility of gradual architecture evolution

---

## 5. Authentication and Authorization

The authentication subsystem implements the following functionality:

- registration via email + password
- login via **Google OAuth**
- secure password storage (hashing)
- **JWT authentication**
- account confirmation via email
- password recovery
- potential **2FA** support in the future
- **superuser (Django default)** role for administrative operations

Authorization will be based on:

- entity access rights verification
- user role separation (User, Moderator/Admin)

---

## 6. Background Processing (Celery)

For executing long-running and deferred tasks, the following stack is used:

- **Celery**
- message broker — **RabbitMQ or Redis**

Main task classes:

- soft-deleted entry cleanup
- image processing (thumbnail generation, resize)
- sending email notifications (registration confirmation, password recovery)
- periodic statistics recalculation

This allows offloading the API and improving system responsiveness.

---

## 7. Data Storage

Storage is divided into two levels:

1. **PostgreSQL (metadata):**
    - users
    - entries (Entry)
    - photos (Photo)
    - statuses, attributes, timestamps

    Special emphasis:

    - indexes on user, creation date, status
    - schema normalization
    - query optimization
2. **S3-compatible object storage**
    - DigitalOcean Spaces / MinIO
    - storing original images
    - possible storage of derived versions (thumbnails)

---

## 8. Logging and Monitoring

The logging system includes:

- log output to stdout under Docker
- file rotation when necessary
- structured event records
- exception handling at service level

For advanced monitoring, possible integration:

- **Sentry** — application error collection
- metrics and alerts for critical failures

---

## 9. Frontend Architecture

The frontend will be implemented as a **React-based SPA** with the following stack:

- React + styled-components
- **TypeScript** (optional, for typing practice)
- API client module for working with backend API
- separation into:
    - pages (views)
    - UI components
    - forms
    - state services

UX and behavior features:

- proper validation error handling
- photo upload error display
- operation status notifications
- clean navigation and state management

Future possible integrations:

- SSR / hydration
- mobile client or PWA
- alternative UI libraries

---

## 10. Deployment and CI/CD

Deployment is planned on DigitalOcean VPS using:

- **Docker + docker-compose**
- services:
    - `web` (Django + gunicorn)
    - `db` (PostgreSQL)
    - `redis / rabbitmq`
    - `nginx`
    - `storage` (MinIO locally)
- Nginx performs:
    - reverse-proxy
    - static file serving
    - TLS termination

Also planned:

- **CI/CD pipeline**
- image building and publishing
- database migrations on deployment
- regular **PostgreSQL backups** to object storage