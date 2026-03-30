# C4 Component Diagram - AI Agent

```mermaid
C4Component
    title Component Diagram for AI Agent

    Container_Ext(objectStorage, "Object Storage", "S3/MinIO")
    Container_Ext(llmProvider, "LLM Provider", "OpenAI")
    Container_Ext(backendApi, "Backend API", "Django Service")
    
    Container_Boundary(entryPointBoundary, "Entry Point") {
        Component(queueConsumer, "Queue Consumer", "Celery Worker", "Receives tasks from queue")
    }
    
    Container_Boundary(coreLayerBoundary, "Core Layer") {
        Component(agentOrchestration, "Agent Orchestration", "LangGraph, LangChain", "Manages execution flow")
        Component(promptBuilder, "Prompt Builder", "Python", "Composes LLM prompts")
    }
    
    Container_Boundary(executionLayerBoundary, "Execution Layer") {
        Component(reasoningLoop, "Reasoning Loop", "LangGraph", "Iterative thought action cycle")
        Component(toolSet, "Tool Set", "Python", "OCR, extractors, checks")
        Component(llmRegistry, "LLM Registry", "LangGraph", "Manages LLM connections")
    }
    
    Container_Boundary(dataLayerBoundary, "Data Layer") {
        ContainerDb(procedureDatabase, "Procedure Database", "SQLite", "Stores data only about the procedures")
        System_Ext(knowledgeBase, "Knowledge Base", "Detailed info about procedures in certain formats")
    }
    
    Container_Boundary(outputBoundary, "Output") {
        Component(callbackClient, "Callback Client", "Python", "Sends results back to Backend API")
    }

    Rel(queueConsumer, agentOrchestration, "Triggers")
    Rel(agentOrchestration, promptBuilder, "Requests prompt")
    Rel(agentOrchestration, procedureDatabase, "Loads procedure (record + document)")
    Rel(agentOrchestration, reasoningLoop, "Executes")
    Rel(agentOrchestration, objectStorage, "Fetches document")
    Rel(agentOrchestration, callbackClient, "Sends report")
    Rel(reasoningLoop, llmRegistry, "Calls LLM")
    Rel(reasoningLoop, toolSet, "Uses tools")
    Rel(llmRegistry, llmProvider, "API calls")
    Rel(procedureDatabase, knowledgeBase, "Corresponds with")
    Rel(callbackClient, backendApi, "POST callback")
```

## Description

This Component diagram shows the internal structure of the AI Agent system:

### Entry Point Layer
- **Queue Consumer**: Celery Worker that receives tasks from the message queue and triggers the agent orchestration

### Core Layer
- **Agent Orchestration**: LangGraph/LangChain component that manages the overall execution flow
- **Prompt Builder**: Python component that composes prompts for the LLM
- **Callback Client**: Handles communication back to the Backend API

### Execution Layer
- **Reasoning Loop**: LangGraph component implementing iterative thought-action cycles
- **Tool Set**: Python components providing OCR, extractors, and validation checks
- **LLM Registry**: Manages connections to different LLM providers

### Data Layer
- **Procedure Database**: SQLite database storing procedure information
- **Knowledge Base**: External system with detailed procedure information

### Output Layer
- **Callback Client**: Sends results back to the Backend API

### Data Flow
1. Queue Consumer receives tasks and triggers Agent Orchestration
2. Agent Orchestration loads procedures from Procedure Database
3. Agent Orchestration fetches documents from Object Storage
4. Agent Orchestration requests prompts from Prompt Builder
5. Agent Orchestration executes Reasoning Loop
6. Reasoning Loop calls LLM via LLM Registry
7. Reasoning Loop uses tools from Tool Set
8. Results are sent back via Callback Client to Backend API