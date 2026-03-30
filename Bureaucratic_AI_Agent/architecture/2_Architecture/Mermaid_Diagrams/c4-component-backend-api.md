# C4 Component Diagram - Backend API

```mermaid
C4Component
    title Component Diagram for Backend API

    Container_Boundary(apiLayerBoundary, "API Layer") {
        Component(authApi, "Auth API", "DRF, Djoser, JWT", "Handles authentication")
        Component(sseEndpoint, "SSE Endpoint", "Django Streaming", "Real-time notifications")
        Component(applicationApi, "Application API", "DRF Generic Views", "Handles authentication")
        Component(callbackApi, "Callback API", "DRF APIView", "Handles callback from the AI agent")
    }
    
    Container_Boundary(serviceLayerBoundary, "Service Layer") {
        Component(applicationService, "Application Service", "Python, ABC", "Services application business logic")
        Component(reportService, "Report Service", "Python, ABC", "Report processing")
        Component(tasksService, "Tasks Service", "Python, ABC", "Handles integration with the task queue")
    }
    
    Container_Boundary(dataLayerBoundary, "Data Layer") {
        Component(djangoModels, "Django Models", "Django ORM", "User, Application, Document, AIReport")
        ContainerDb(relationalDatabase, "Relational Database", "PostgreSQL", "Stores data within Backend API")
    }
    
    Container_Boundary(infrastructureBoundary, "Infrastructure") {
        Component(taskQueueClient, "Task Queue Client", "Celery", "Pushes tasks to the queue")
        Component(storageClient, "Storage Client", "S3 SDK", "File operations")
    }

    Rel(applicationApi, applicationService, "Uses")
    Rel(applicationService, djangoModels, "Uses")
    Rel(reportService, djangoModels, "Uses")
    Rel(djangoModels, relationalDatabase, "Reads/writes")
    Rel(applicationService, tasksService, "Publishes tasks")
    Rel(tasksService, taskQueueClient, "Sends tasks")
    Rel(applicationService, storageClient, "Uploads files")
    Rel(callbackApi, reportService, "Uses")
```

## Description

This Component diagram shows the internal structure of the Backend API system:

### API Layer
- **Auth API**: Django REST Framework with Djoser and JWT for handling authentication
- **SSE Endpoint**: Django Streaming for real-time notifications to clients
- **Application API**: DRF Generic Views for handling application CRUD operations
- **Callback API**: DRF APIView for handling callbacks from the AI Agent

### Service Layer
- **Application Service**: Python service implementing application business logic with Abstract Base Classes
- **Report Service**: Python service for processing AI reports
- **Tasks Service**: Python service handling integration with the task queue (Celery)

### Data Layer
- **Django Models**: ORM models including User, Application, Document, and AIReport
- **Relational Database**: PostgreSQL database storing all backend data

### Infrastructure Layer
- **Task Queue Client**: Celery client for pushing tasks to the message queue
- **Storage Client**: S3 SDK for file operations with Object Storage

### Data Flow
1. API endpoints receive requests from clients
2. API Layer routes to appropriate Services
3. Services use Django Models for data operations
4. Django Models interact with PostgreSQL database
5. Application Service publishes tasks via Tasks Service to Task Queue Client
6. Application Service uploads files via Storage Client
7. Callback API uses Report Service to process AI agent results