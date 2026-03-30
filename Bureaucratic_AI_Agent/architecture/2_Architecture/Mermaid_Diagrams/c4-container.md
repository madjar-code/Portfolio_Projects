# C4 Container Diagram - Bureaucratic AI Agent System

```mermaid
C4Container
    title Container Diagram for Bureaucratic AI Agent System

    Person(user, "User", "Regular citizen")
    
    System_Boundary(backendApiBoundary, "Backend API") {
        Container(backendApiCore, "Backend API Core", "Django + DRF", "HTTP Endpoints, business logic, etc.")
        Container(sseServer, "SSE Server", "Django Streaming", "Real-time notifications")
        Container(taskProducer, "Task Producer", "Celery", "Queue integration")
    }
    
    System_Boundary(aiAgentBoundary, "AI Agent") {
        Container(taskConsumer, "Task Consumer", "Celery Worker", "Receives tasks")
        Container(agentCore, "Agent Core", "LangChain, LangGraph, etc.", "LLM orchestration")
        Container(proceduresDb, "Procedures DB", "SQLite", "Stores Instructions")
    }
    
    System_Boundary(infrastructureBoundary, "Infrastructure") {
        ContainerDb(postgresql, "PostgreSQL", "Relational DB", "App, document, user data")
        ContainerDb(messageQueue, "Message Queue", "Redis/RabbitMQ", "Task queue")
        ContainerDb(objectStorage, "Object Storage", "S3/MinIO", "Stores files locally or remotely")
    }
    
    Container(webClient, "Web Client (SPA)", "NextJS, TypeScript", "User interface")
    
    System_Ext(openaiApi, "OpenAI API", "GPT-4, and similar")
    System_Ext(mockExternalApi, "Mock External API", "External validation")

    Rel(user, webClient, "Uses")
    Rel(webClient, backendApiCore, "HTTPS", "REST Calls")
    Rel(sseServer, webClient, "Push events", "SSE")
    Rel(backendApiCore, postgresql, "CRUD operations")
    Rel(backendApiCore, taskProducer, "Submit tasks")
    Rel(backendApiCore, objectStorage, "Manage files")
    Rel(taskProducer, messageQueue, "Publish tasks")
    Rel(taskConsumer, messageQueue, "Consume")
    Rel(taskConsumer, agentCore, "Execute")
    Rel(agentCore, proceduresDb, "Load procedure")
    Rel(agentCore, objectStorage, "Fetch document")
    Rel(agentCore, openaiApi, "Fetch document")
    Rel(agentCore, mockExternalApi, "Fetch document")
```

## Description

This Container diagram shows the detailed architecture of the Bureaucratic AI Agent system:

### Backend API Subsystem
- **Backend API Core**: Django + DRF application handling HTTP endpoints and business logic
- **SSE Server**: Django Streaming for real-time notifications to the web client
- **Task Producer**: Celery integration for publishing tasks to the message queue

### AI Agent Subsystem
- **Task Consumer**: Celery Worker that receives tasks from the queue
- **Agent Core**: LangChain/LangGraph orchestration for LLM processing
- **Procedures DB**: SQLite database storing instructions

### Infrastructure
- **PostgreSQL**: Main relational database for application, document, and user data
- **Message Queue**: Redis/RabbitMQ for task queue management
- **Object Storage**: S3/MinIO for file storage

### External Systems
- **OpenAI API**: GPT-4 and similar LLM services
- **Mock External API**: External validation service

### Data Flow
1. User interacts with Web Client (SPA)
2. Web Client communicates with Backend API Core via HTTPS/REST
3. Backend API Core manages data in PostgreSQL and files in Object Storage
4. Backend API Core publishes tasks via Task Producer to Message Queue
5. Task Consumer retrieves tasks and triggers Agent Core
6. Agent Core loads procedures from Procedures DB and fetches documents
7. Agent Core communicates with external APIs (OpenAI, Mock External API)
8. Results are returned via SSE Server for real-time updates