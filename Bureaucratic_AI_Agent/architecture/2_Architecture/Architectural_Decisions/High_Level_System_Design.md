![High Level System Design](../Pictures/High_Level_System_Design.webp)

## **1. Overview**

The system is designed for automating the processing of user applications, including metadata and documents. The architecture is built on separation of responsibilities between the backend, which manages the application lifecycle, and the AI agent, which performs the processing.

The key idea of the system is asynchronous task processing with an explicit feedback loop: the backend initiates processing, and the agent returns the result upon completion via callback.

## **2. Architectural Approach**

The system is built around asynchronous interaction between components through a message queue.

The backend is responsible for:

- receiving and storing applications,
- queuing tasks for processing,
- state management.

The AI agent acts as an independent worker that processes tasks and returns results via **callback to the backend**.

It is the callback model that makes the system reactive and allows the backend to remain the source of truth for application states.

## **3. System Components**

### **3.1 Web Client (SPA)**

The user interacts with the system through a web application where they can create applications, upload documents, and track the status of their processing.

All business logic is concentrated on the backend, and the client is only responsible for displaying and sending data.

### **3.2 Backend API**

The backend is the central orchestrator of the system.

After receiving an application, the backend:

1. authenticates the user and validates data,
2. saves metadata to PostgreSQL,
3. uploads the file to Object Storage,
4. forms a task and sends it to the queue.

After the agent processes the application, the backend receives the result via callback API. Upon receiving the report, the backend:

- saves it,
- updates the application status,
- initiates user notification (e.g., via SSE).

Thus, the backend fully controls the system state and does not delegate state storage to the agent.

### **3.3 Task Queue**

The message queue provides asynchronous interaction between the backend and the agent.

It allows:

- processing tasks with delay,
- scaling workers,
- retrying execution on failures.

The queue transfers to the agent only the task description and necessary links/identifiers, without transferring state.

### **3.4 AI Agent**

The AI agent is an independent worker that extracts tasks from the queue and executes them.

The processing process includes:

- receiving and interpreting the task,
- downloading and analyzing the document,
- performing validations and external checks,
- forming a structured report.

After processing is complete, the agent sends the result back to the backend via **HTTP callback**. This is a key point: the agent does not change state directly, but reports the result, leaving the backend responsible for recording changes.

### **3.5 Agent Logic and Data**

The application processing logic is defined through procedures stored in a separate agent database (SQLite). This allows changing system behavior without modifying the backend.

The agent uses:

- tools for document processing,
- validation mechanisms,
- external requests to a mock service,
- knowledge base for context.

This approach makes processing declarative and extensible.

### **3.6 Data Storage**

The system uses several types of storage:

- **PostgreSQL** — storage of users, applications, and reports
- **Object Storage** — file storage
- **SQLite (Agent DB)** — processing procedures
- **Knowledge Base / Document DB** — auxiliary data for the agent

Separation of storage allows independent scaling of different parts of the system.

## **4. Data Flow**

The main processing scenario:

1. User creates an application through SPA
2. Backend saves data and file
3. Backend sends a task to the queue
4. AI agent receives the task and performs processing
5. Agent sends the result to the backend via callback
6. Backend saves the report and updates the status
7. User receives an update

The key feature is **two-way asynchronous communication**: the task is transferred through the queue, and the result is returned via callback.

## **5. Communication Model**

The system uses several interaction models:

- synchronous: client ↔ backend (REST API)
- asynchronous: backend → queue → agent
- callback: agent → backend (HTTP callback)
- push notifications: backend → client (SSE/WebSocket)

This separation allows efficient processing of long operations without blocking the interface.

## **6. Key Design Decisions**

The key decision is using a callback mechanism for returning processing results. This allows the agent to remain isolated and independent of the backend's internal data model.

Another important decision is separating the agent into an independent service. This provides the ability to independently scale application processing and evolve AI logic.

The system also separates storage by data types, which simplifies maintenance and scaling.

## **7. Non-Functional Considerations**

The system is oriented toward horizontal scaling by increasing the number of agents.

Reliability is ensured by task retry mechanisms and the fact that the backend remains the single source of truth.

Security is achieved through access control, component isolation, and limited data access.

## **8. Future Evolution**

Possible development directions:

- multi-agent architecture,
- procedure versioning,
- integration with real external services,
- adding manual review stages.
