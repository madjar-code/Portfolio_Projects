## **1. Overview**

The Backend API is the central component of the system and serves as an orchestrator. It is responsible for managing the application lifecycle, user interaction, and coordinating processing through the AI agent.

The backend does not contain document analysis logic — its task is to receive, store, and route data, as well as ensure reliable and consistent system state.

The key architectural principle is separation of responsibilities: the backend manages state, and processing is delegated to an external AI agent through an asynchronous task queue.

## **2. Technology Stack**

The backend is implemented using a Django stack, oriented toward fast development and reliable data handling.

Main components:

- **Django** — main web framework
- **Django REST Framework (DRF)** — API construction
- **PostgreSQL** — main database
- **Django ORM** — database operations
- **Django Migrations** — database schema management
- **Object Storage (S3 / MinIO)** — file storage
- **Task Queue (Celery + RabbitMQ)** — asynchronous tasks

This stack allows building scalable APIs with minimal infrastructure code and high development speed.

## **3. Architectural Layers**

Despite Django-style organization, the system maintains logical separation of responsibilities.

### **API Layer (Views / DRF)**

Responsible for handling HTTP requests. Here occurs:

- routing (urls.py),
- input data validation (serializers),
- authentication and permissions,
- transforming requests into business logic calls.

This layer remains thin and does not contain complex logic.

### **Service Layer (Services / Domain Logic)**

Although Django by default does not require a service layer, in this system it is used explicitly.

It is responsible for:

- business rule validation,
- application lifecycle management,
- model coordination,
- task queuing,
- handling callbacks from the AI agent.

Business logic **is not placed in views or models**, but is centralized in services.

> **Note:** In the current implementation, business logic lives primarily in views and Celery tasks. A dedicated service layer is planned for future refactoring.

### **Data Access Layer (Django ORM)**

Database operations are performed through Django ORM.

Features:

- models are the source of truth for the database schema
- QuerySet is used as the main selection tool
- transactions are managed through `transaction.atomic`

A separate repository layer is not distinguished, as Django ORM already encapsulates data access.

### **Infrastructure Layer**

Contains integrations with external systems:

- task queue (Celery),
- object storage,
- Django settings configuration,
- external clients.

This layer isolates infrastructure details from business logic.

## **4. Backend API Structure**

The Backend API is organized as a monolithic Django application with a modular structure based on domain applications (apps).

The structure reflects the main business domains and uses Django conventions, while maintaining explicit separation of responsibilities within each module:

- `apps/` — domain applications (auth and applications, possibly others later)
- `api/` — API layer (views, serializers, endpoints)
- `services/` — business logic and process orchestration
- `models.py` — ORM models (within each app)
- `managers.py` — custom QuerySets and model managers
- `tasks/` — asynchronous tasks (Celery)
- `migrations/` — database migrations (per app)
- `admin.py` — Django admin panel

Common and reusable components:

- `common/` — common utilities, exceptions, base classes
- `config/` — project configuration (settings, environment-specific settings)
- `storage/` — Object Storage integration
- `queue/` — task queue integration

Entry point:

- `manage.py` — CLI for project management
- ASGI/WGI configuration — application startup

Additionally:

- `tests/` — tests (unit and integration)
- `.env` / settings modules — environment configuration (dev/prod)

This approach combines:

- **Django conventions (apps, models, admin)**
- **explicit business logic separation (services)**
- **domain-based modularity**

and ensures good readability, scalability, and system maintainability.

## **5. API Design Principles**

The API is designed with extensibility and consistency in mind.

Main principles:

- versioning (`/api/v1/...`)
- use of DRF serializers
- pagination support
- unified error format
- health-check endpoint presence
- rate limiting (through DRF or middleware)

Error handling is centralized through Django exception handling and DRF.

## **6. Core Flows**

### **6.1 Application Submission Flow**

The application submission process is divided into several stages.

First, the user creates an application in `DRAFT` status. Then they upload a document, which is saved in Object Storage, and its metadata is recorded in the database. After that, the user fills out a form, the data of which is saved in the model's JSON field.

The final step is submitting the application (`submit`). At this stage, the service layer:

- validates data correctness
- transitions the application to `SUBMITTED` status
- initiates an asynchronous task

After that, the task is sent to the queue (Celery), and the client receives `202 Accepted`.

When processing begins, the application status is updated to `PROCESSING`.

### **6.2 AI Callback Flow**

After processing is complete, the AI agent sends the result via callback API.

The backend:

- accepts a POST request (DRF view)
- performs authentication via HMAC-SHA256 (`X-Signature` + `X-Timestamp` headers)
- validates data (serializer)

Then the service layer:

- checks application existence
- saves the report (within `transaction.atomic`)
- updates the status:
    - `APPROVED`
    - `REJECTED`
- records processing time

After successful processing, `200 OK` is returned.

### **6.3 Real-Time Notifications (SSE)**

Server-Sent Events (SSE) mechanism is used for user notifications.

Django can use:

- streaming responses
- or a separate ASGI layer (e.g., Django Channels)

The backend:

- maintains the connection
- sends events when application status changes

This allows updating the interface without polling.

## **7. Task Queue Integration**

The backend uses Celery for transferring tasks to the AI agent.

The task contains:

- application identifier
- metadata
- `doc_url`

Celery provides:

- asynchronicity
- retry mechanism
- fault tolerance

When attempts are exhausted:

- the application transitions to `FAILED`
- then is mapped to user status

## **8. Database Integration**

Database operations are implemented through Django ORM.

Key aspects:

- use of connection pooling (at PostgreSQL level)
- transactions through `transaction.atomic`
- use of select_related / prefetch_related for optimization

Transactions are applied in operations where consistency is important:

- creating application and document
- saving report and updating status

## **9. File Storage**

User files are stored in Object Storage.

- **MinIO** — for local development
- **S3** — for production

Integration is performed through Django storage backend.

The backend:

- validates files
- manages access
- stores only links (URLs)

## **10. Security**

Security is implemented at multiple levels.

- JWT (through DRF or third-party libraries)
- password hashing (built-in Django mechanism)
- file validation
- callback API protection through API key

Secrets:

- `.env` (dev)
- secrets manager (prod)

## **11. Error Handling and Observability**

The system uses centralized error handling.

- DRF exception handler
- custom exceptions
- unified response format

Logging:

- Django logging config
- requests
- errors
- business events

Integration with monitoring and alerting systems is possible.

## **12. Summary**

The Backend API is designed as a Django-based orchestrator that manages system state and delegates processing to the AI agent.

The asynchronous model using Celery and callback allows efficient processing of long operations and system scaling.

The use of Django apps, ORM, and built-in framework mechanisms simplifies development, increases reliability, and makes the system convenient for further development.
