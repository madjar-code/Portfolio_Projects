## **1. Overview**

The frontend is a thin, stateless client that talks to one backend. It has no business logic of its own — it displays data, captures user input, and reflects system state in real time. Complexity lives on the backend; the frontend's job is to surface that complexity clearly and responsively.

The stack is **TypeScript + React** for the UI, **Axios** for HTTP requests, and **Tailwind CSS** for styling. These choices favour explicitness and a small dependency surface: TypeScript catches contract mismatches between the API and the UI at compile time; Axios provides a consistent interceptor layer for auth token injection; Tailwind keeps styles co-located with the components that use them.

The design rests on three constraints:

- **Lightweight.** The frontend does not own any domain decisions. It renders what the backend returns and submits what the user provides.
- **Real-time.** Application status changes asynchronously — processing happens on the backend. The client must reflect those changes without polling.
- **Explicit structure.** The gap between data fetching and UI rendering is never implicit. Every concern — HTTP requests, state updates, presentation — has a named home in the project tree.

---

## **2. Authentication**

The client handles three token operations: **login**, **logout**, and **silent refresh**. These are the only authentication responsibilities the frontend carries — authorization decisions are made and enforced on the backend.

Tokens are stored in a way that survives a page reload but is not accessible to third-party scripts. Every outbound HTTP request carries the current access token. When a request fails with an unauthenticated response, the client attempts a silent refresh before surfacing the error to the user. If the refresh fails, the session is terminated and the user is returned to the login page.

**Principle:**

> The frontend is not a trust boundary. It holds credentials only long enough to attach them to requests. The backend decides whether those credentials are valid.

---

## **3. Pages and Routing**

The application has a small, fixed set of pages. Each corresponds to a distinct user intent and maps onto a distinct backend resource.

### **3.1 Applications Index**

The entry point of the authenticated experience. Displays the list of the user's applications — each with its summary fields and current status. This page answers: *"What have I submitted, and where does each stand?"*

### **3.2 Application Detail**

Displays the full record for a single application: form data, document reference, lifecycle status, and — once processing is complete — the full AI-generated report. This page answers: *"What did the system decide, and why?"*

The FAILED state is displayed distinctly from REJECTED. The first is a reliability outcome; the second is a domain decision. Users see both, but the labels and copy distinguish them.

### **3.3 Application Create**

A form page. The user selects a procedure, fills in the required fields, and uploads a document. On submission the form data and file are sent together in a single multipart request. The page is intentionally minimal — it mirrors the shape of the backend's create endpoint without adding client-side validation beyond what the backend would reject anyway.

**Principle:**

> Validate at the boundary that enforces the rule. Duplicating backend validation on the frontend produces two code paths that drift apart.

### **3.4 Application Submit**

Submission is a separate, explicit step: the user reviews the created application and confirms they want it sent for AI processing. This maps onto a distinct backend endpoint and produces a distinct status transition. The two-step flow prevents accidental submissions and makes the point of no return visible.

---

## **4. Data Transport**

The frontend communicates with the backend over two channels that serve different purposes and are never merged.

### **4.1 HTTP (request/response)**

All read and write operations follow the standard request/response pattern: listing applications, fetching a detail, creating a record, submitting for processing. Requests are made through a service layer (see §6) that handles auth token injection, error normalisation, and request cancellation.

### **4.2 SSE (server-sent events)**

Application status changes are delivered over a persistent SSE connection. The client opens this connection once, after login, and keeps it open for the session. When a status update arrives, the client updates local state without issuing a new HTTP request.

SSE is one-directional: the server pushes, the client listens. This is intentional — the client has nothing to send over this channel. A bidirectional channel would add complexity without benefit for this use case.

**Principle:**

> HTTP describes what is; SSE describes what changed. Each channel does one thing, and neither substitutes for the other.

The SSE connection is treated as best-effort: a dropped connection triggers a reconnect attempt. If the connection is down when a status change occurs, the client falls back to an HTTP fetch on reconnect to reconcile its local state.

---

## **5. State Management**

The client holds two categories of state:

- **Server state** — data that originates from the backend: application lists, detail records, AI reports. This state is fetched, cached locally, and invalidated when the server signals a change (via SSE or after a mutation).
- **UI state** — form values, loading flags, open/closed panels. This state is local to the component that owns it and does not cross component boundaries unless explicitly lifted.

The two categories are kept separate. Server state synchronisation logic does not live inside components; it lives in hooks that components consume. A component that displays an application record does not know how that record was fetched or when it was last refreshed.

**Principle:**

> A component that fetches its own data couples presentation to transport. Separating them means the same component can be driven by a network response, a cache hit, or a test fixture without change.

---

## **6. Project Structure**

The project tree has four named layers. Each layer has a single responsibility and depends only on layers below it.

```
src/
  pages/        # Route-level components. Compose smaller components; own no local state beyond what routing requires.
  components/   # Reusable UI units. Receive data via props; emit events via callbacks. No direct API calls.
  hooks/        # Encapsulate data-fetching logic, SSE subscription, and derived state. Return clean interfaces for pages and components to consume.
  services/     # Raw HTTP and SSE clients. No React. Configures auth headers, base URL, error normalisation.
```

The dependency direction is strict: `pages → components`, `pages/components → hooks`, `hooks → services`. A component that imports a service directly, or a service that imports a hook, is a structural error.

**Principle:**

> Structure is documentation. When the layer boundary is clear, the right place for new code is obvious without discussion.

---

## **7. Error Handling**

Errors are classified at the service layer before they reach component code:

- **Network errors** — no response received. The client shows a connection problem message and, where appropriate, retries.
- **Authentication errors** — 401 responses trigger silent token refresh; on failure, session is cleared.
- **Validation errors** — 4xx responses from create/submit endpoints carry field-level error detail. These are surfaced inline in the relevant form.
- **Server errors** — 5xx responses are shown as generic failure messages. The backend's structured error body is logged for debugging but not shown to users.

Error boundaries prevent a failed subtree from taking down the full page. Each page that contains independent sections wraps them individually so that a failed AI report panel does not hide the application summary.

---

## **8. Summary**

- **The frontend is a rendering layer, not a logic layer.** Business rules, validation, and processing decisions live entirely on the backend.
- **Two channels, one purpose each.** HTTP for request/response operations, SSE for real-time status delivery. Neither replaces the other.
- **Authentication is minimal and delegated.** The client carries tokens and refreshes them; it never makes trust decisions.
- **Four structural layers, one direction of dependency.** Pages, components, hooks, services — each with a single responsibility, no upward imports.
- **State has two kinds.** Server state is synchronised; UI state is local. They are managed separately and never mixed.
- **Errors are classified, not just caught.** Each error class has a defined outcome visible to the user, with no silent drops.
