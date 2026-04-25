# C4 Context Diagram - Bureaucratic AI Agent System

```mermaid
C4Context
    title System Context Diagram for Bureaucratic AI Agent System

    Person(user, "User", "Regular citizen")
    
    System(webClient, "Web Client (SPA)", "User interface for creating and tracking applications")
    System(backendApi, "Backend API", "Manages application lifecycle, user data, and orchestrates processing")
    System(aiAgent, "AI Agent", "Processes applications using LLM and validates documents")
    System(objectStorage, "Object Storage", "S3/MinIO - stores user documents")
    System(llmProvider, "LLM Provider", "OpenAI / Anthropic")
    System(mockExternalApi, "Mock External API", "External validation")
    
    System_Boundary(bureaucraticSystem, "Bureaucratic App System") {
        System(webClient)
        System(backendApi)
        System(aiAgent)
    }

    Rel(user, webClient, "Uses")
    Rel(webClient, backendApi, "Submits applications, view reports", "HTTPS/REST, SSE")
    Rel(backendApi, objectStorage, "Stores/retrieves documents", "S3 API")
    Rel(backendApi, aiAgent, "Sends tasks", "Task Queue")
    Rel(aiAgent, backendApi, "Returns results", "HTTP Callback")
    Rel(aiAgent, objectStorage, "Fetches documents", "S3 API")
    Rel(aiAgent, llmProvider, "Requests analysis", "HTTP/API")
    Rel(aiAgent, mockExternalApi, "Validates Data", "HTTP/REST")
```

## Description

This Context diagram shows the high-level view of the Bureaucratic AI Agent system:

- **User**: A regular citizen who interacts with the system
- **Web Client (SPA)**: Single-page application built with React/TypeScript (Vite) that provides the user interface
- **Backend API**: Core system that manages applications, user data, and orchestrates processing
- **AI Agent**: Intelligent component that processes applications using LLM and validates documents
- **Object Storage**: S3/MinIO storage for user documents
- **LLM Provider**: OpenAI (gpt-4o-mini default) / Anthropic, configurable via `DEFAULT_MODEL`
- **Mock External API**: External validation service

The system boundary "Bureaucratic App System" encompasses the main components that make up the application.