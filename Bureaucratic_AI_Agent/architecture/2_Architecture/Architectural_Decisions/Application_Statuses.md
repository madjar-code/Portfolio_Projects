## **1. Overview**

The application lifecycle is modeled as a finite state machine with fixed states — from creation to processing result.

Each application:

- is processed once,
- does not support resubmission,
- ends in one of the final states.

## **2. State Diagram**

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    
    DRAFT --> DRAFT: Form/document update
    DRAFT --> SUBMITTED: POST /applications/{id}/submit

    SUBMITTED --> PROCESSING: Agent pulls task from queue

    PROCESSING --> FAILED: System error (user does not see this status)

    PROCESSING --> REJECTED: AI validation rejected
    PROCESSING --> APPROVED: AI validation passed

    FAILED --> PROXY_STATUS: Hide problem from user
    PROXY_STATUS --> [*]
    REJECTED --> [*]
    APPROVED --> [*]
```

## **3. States**

- **DRAFT** — application creation and editing
- **SUBMITTED** — application passed initial validation and sent for processing
- **PROCESSING** — agent is processing the application
- **FAILED (internal)** — system error (not shown to user)
- **REJECTED** — application rejected based on AI validation results
- **APPROVED** — application successfully passed verification
- **PROXY_STATUS** — user-facing error representation

## **4. Flow Summary**

1. `DRAFT → SUBMITTED` — user submits the application
2. `SUBMITTED → PROCESSING` — agent starts processing
3. Possible outcomes:
    - `PROCESSING → APPROVED`
    - `PROCESSING → REJECTED`
    - `PROCESSING → FAILED → PROXY_STATUS`

Final states: `APPROVED`, `REJECTED`, `PROXY_STATUS`.

## **5. Notes**

- Backend is the single source of truth for status
- `FAILED` is used only internally within the system
- The model is simplified by the absence of retry / resubmission
