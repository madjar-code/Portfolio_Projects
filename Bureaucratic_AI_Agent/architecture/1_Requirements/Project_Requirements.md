This document details the functional and non-functional requirements for the bureaucratic agent project.


## 1. Goals and Scope

| **Type** | **Description** |
| --- | --- |
| Main Goal | Create a web platform that allows accepting applications from citizens with a bureaucratic agent on the backend. |
| In Scope | Authentication (simple), application submission (form + documents), viewing application status, receiving feedback on applications, application processing on the backend (metadata and documents). |
| Out of Scope | Interactive sessions with AI agent, including bureaucrat in sessions, complex multi-stage scenarios, integrations with real services, … |

---

## 2. User and Authentication Requirements

### 2.1 Authentication Functional Requirements (FR-AUTH)

| ID | Requirement | Role | Notes |
| --- | --- | --- | --- |
| FR-AUTH-100 | The system must allow the user to log in using email and password. | Citizen | JWT tokens for sessions. |
| FR-AUTH-101 | The system must allow the user to log out of their account. | Citizen | Token invalidation on the client side. |
| FR-AUTH-102 | The system must restrict access to applications to their owner only. | Citizen | The user can only see their own applications. |

### **2.2 User Management Functional Requirements (FR-USER)**

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-USER-200 | The user must be able to view their profile (email, authorization date). | Citizen | Basic user information. |

---

## **3. Application Functional Requirements**

### **3.1 Application Creation and Submission (FR-APP)**

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-APP-100 | The system must allow the user to create a new application with procedure type selection. | Citizen | Selection from a predefined list of procedures (e.g., "Passport issuance", "Individual entrepreneur registration"). |
| FR-APP-101 | The system must allow the user to fill out an application form with required fields. | Citizen | Fields depend on the procedure type (dynamic form). |
| FR-APP-102 | The system must allow the user to upload a document to the application (PDF, DOCX, JPG, PNG). | Citizen | Currently only one document. Multiple upload capability will be added later. |
| FR-APP-103 | The system must validate the completed form before submission. | System | Validation of required fields, data format (email, phone, tax ID, etc.). |
| FR-APP-104 | The system must allow the user to submit the application for processing. | Citizen | After submission, the application receives "Under Review" status. |
| FR-APP-105 | The system must generate a unique application number upon creation. | System | Format: APP-YYYYMMDD-XXXXX. |

### 3.2 Application Viewing and Management (FR-APP)

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-APP-200 | The system must allow the user to view a list of their applications. | Citizen | Pagination, sorting by creation date, filtering by status. |
| FR-APP-201 | The system must allow the user to open an application detail page. | Citizen | View all application data, uploaded documents, status history. |
| FR-APP-202 | The system must allow the user to cancel an application before processing begins. | Citizen | Not yet implemented. |
| FR-APP-203 | The system must display the current application status. | Citizen | Statuses: DRAFT, SUBMITTED, PROCESSING, APPROVED, REJECTED, FAILED. |

### **3.3 AI Agent Application Processing (FR-AGENT)**

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-AGENT-300 | The system must automatically check the application for completeness upon submission. | AI Agent | Verification of all required fields and documents according to the procedure checklist. |
| FR-AGENT-301 | The system must adapt to different verification scenarios based on existing documentation of bureaucratic processes | AI Agent | That is, we are not creating a static workflow. We are creating an agent that reads information about a particular bureaucratic process and performs actions based on it. |
| FR-AGENT-302 | The system must automatically extract data from uploaded documents (OCR/parsing). | AI Agent | Extraction of names, dates, document numbers from PDF/images. |
| FR-AGENT-303 | The system must generate an application verification report and send feedback to the user | AI Agent | List of found issues or confirmation of correctness. Also a clear description of what needs to be corrected or supplemented. |
| FR-AGENT-304 | The system must automatically change the application status based on verification results | AI Agent |  |

---

## 4. Knowledge Base Functional Requirements

### 4.1 **Procedure Management (FR-PROCEDURE)**

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-PROCEDURE-400 | The system must store descriptions of bureaucratic procedures. | System | Name, description, required documents, deadlines, cost. |
| FR-PROCEDURE-401 | The system must allow the user to view a list of available procedures. | Citizen | Procedure catalog with descriptions. |
| FR-PROCEDURE-402 | The system must store checklists for each procedure. | System | List of required fields and documents. |
| FR-PROCEDURE-403 | The agent uses procedure descriptions for dynamic verification and tool usage | AI Agent |  |

### **4.2 Document Templates (FR-TEMPLATE)**

> **Not implemented.** Planned for future iteration.

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-TEMPLATE-500 | The system must store document templates for procedures. | System | Application forms, blanks, etc. |
| FR-TEMPLATE-501 | The system must allow the AI agent to automatically fill templates with application data. | AI Agent | Generation of a filled document based on user data. |

---

## 5. Non-Functional Requirements (NFR)

| ID | Description | Category | Notes |
| --- | --- | --- | --- |
| NFR-001 | The system must process applications in the background so that the user does not wait for a response. | Performance | Asynchronous processing, task queues (Celery/RQ). |
| NFR-002 | All operations with personal data must be performed over HTTPS. | Security | SSL/TLS certificates. |
| NFR-003 | Uploaded documents must be stored in encrypted form. | Security |  |
| NFR-004 | The system must log all user and AI agent actions. | Observability | Logs to file/service (Sentry, CloudWatch). |
| NFR-005 | The agent must periodically undergo automatic evaluation. | Evaluation | Evaluation CI/CD. |
| NFR-006 | The interface must be responsive for mobile devices. | Usability | Mobile-first approach in design. |
| NFR-007 | Request spamming must be prevented. | Security | Rate limiter. |

