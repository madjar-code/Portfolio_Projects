## **1. Overview**

The Backend API is instrumented along two independent channels: **logging** and **metrics**. Each answers a different question, lives in its own storage, and is read by a different audience.

- **Logs** capture the full story of **one request** — line by line, with enough context to reconstruct what happened and why.
- **Metrics** capture aggregate behaviour **across many requests** — numeric, time-indexed, stripped of per-request detail.

These two channels are not merged. A log line and a time series answer different questions, require different retention, and tolerate each other's absence gracefully. The system is designed so that losing one does not blind the other.

---

## **2. Logging**

### **2.1 Single stream, structured format**

Every log record is **machine-readable** and carries the same shape regardless of its source (application code, framework internals, request handler). The stream is simultaneously:

- readable by the operator tailing output in a terminal,
- parseable by any downstream consumer without ad-hoc regexes.

**Principle:**

> Either the stream is structured end-to-end, or it isn't structured at all. Mixed formats force every consumer to guess, which defeats the purpose of logging in the first place.

Cosmetic additions from the underlying framework (colour codes, pretty-printed delimiters) are stripped before they enter the structured stream — they belong to the terminal experience, not to the log content.

### **2.2 Request correlation**

Every incoming request is assigned a **correlation identifier** at the outer edge of the request pipeline. The identifier is:

- accepted from the caller if provided (to extend an external trace into the system),
- generated otherwise,
- propagated through request-scoped state so that every log line produced during the request carries it,
- echoed back in the response so the caller can refer to it later.

This gives every log line a join key. With a correlation ID, a scattered sequence of lines about the same request reassembles into a single story; without it, the log is only useful one line at a time.

**Principle:**

> A log without correlation is text. A log with correlation is a graph. The instrumentation effort is small; the cognitive payoff is large.

### **2.3 Where logs live**

Logs are written to two sinks at once:

- a **live stream** intended to be consumed as it's produced (by the operator, by a container runtime, eventually by a log shipper),
- a **local persistent file** with bounded size and rotation, so that recent history is available offline for inspection.

Keeping both sinks simultaneously means neither a crashed shipper nor a missing terminal erases the record.

---

## **3. Metrics**

Metrics describe system behaviour as **numeric series over time**. The API exposes them through a standard pull-based interface, which an external collector polls on a fixed interval.

The metrics are organised into **two tiers** with deliberately different lifecycles.

### **3.1 Infrastructure tier**

Automatic per-endpoint counters and histograms — request rate, response rate by status, latency distribution, database timing. These describe **the transport**: they would exist even if the application had no business domain at all, and are valid for any API of the same shape.

They answer: *"Is the service healthy?"*

### **3.2 Domain tier**

Hand-placed counters and histograms that describe the **application lifecycle** of the system — how often each step of the funnel is entered, how long the full flow takes end-to-end, how outcomes distribute across categories.

They answer: *"Is the product doing what it is supposed to do?"*

**Principle:**

> Infrastructure metrics measure the transport. Domain metrics measure the purpose. They look the same to the collector but belong to different readers — one is an operator, the other is a stakeholder.

### **3.3 Cardinality discipline**

Metrics are cheap only as long as their label sets stay small. The system keeps labels limited to closed, enumerable sets (procedure, decision, status class). Anything open-ended — user identifiers, free text, correlation IDs — never becomes a label.

**Principle:**

> High-cardinality attributes belong in logs, where the cost of more distinct values is linear. In metrics, the cost is multiplicative.

This discipline is what lets the two channels coexist without one bleeding into the other.

### **3.4 Where instrumentation lives**

Domain instrumentation is placed **at the exact code points where the business event happens** — the moment an application is created, submitted, decided. It is kept out of framework-level hooks and signals, which fire at times the developer did not intend (during migrations, admin actions, test setup) and silently contaminate the numbers.

**Principle:**

> Instrumentation that is hidden is instrumentation that lies. Prefer explicit calls at the site of the event, even at the cost of a few extra lines.

---

## **4. Collection and Visualisation**

The API does not store its own metrics. It **exposes** them; a dedicated collector **pulls** them on a schedule and retains them as time series. A separate visualisation layer queries the collector to render dashboards.

Both the collector's scrape configuration and the dashboards are **checked into the repository as declarative files**. They are provisioned automatically on service start and never modified through the UI.

**Principle:**

> Observability configuration is code. Clicking through a UI to define a dashboard produces state that cannot be diffed, reviewed, or reproduced — the same objections that apply to manual database changes.

Dashboards are partitioned along the same split as the metrics themselves:

- one for the **infrastructure tier**, read by operators,
- one for the **domain tier**, read by stakeholders interested in the product.

Splitting them keeps each surface uncluttered and matches the distinct audiences.

---

## **5. Scope and Future Seams**

The design is scoped narrowly on purpose. The following are **intentionally out of the current surface**, not forgotten:

- **Asynchronous workers** (task queue, background processors) are not instrumented yet. The shape of their observability will mirror the API's — structured logs, tiered metrics — but happens as a follow-up.
- **The AI agent** is observed through a separate narrative-oriented channel suited to LLM runs; aligning its metric surface with the API's tier model is a future step.
- **Centralised log shipping** is not in place. The local file plus live stream is sufficient for current scale.
- **Distributed tracing** across service boundaries is not yet implemented. Correlation today is string-based, carried through the correlation ID in logs. Upgrading this to span-based tracing is an isolated extension that does not require rewriting anything already built.

Each item is a **seam**, not a hole: the current architecture admits it without structural change when the need becomes real.

---

## **6. Summary**

The observability of the Backend API rests on a small number of deliberate choices:

- **Two channels, not one** — logs describe single requests; metrics describe aggregate behaviour. They stay separate.
- **Structure from the start** — log records are machine-readable; mixed text/structured streams are avoided.
- **A correlation ID is a first-class requirement** — every request carries one, every log line inherits it, callers can join on it.
- **Two tiers of metrics** — the transport layer and the domain layer, collected uniformly but read by different people.
- **Cardinality is a constraint, not a default** — high-cardinality detail belongs in logs.
- **Instrumentation is explicit** — placed at the code points where meaningful events occur, never hidden inside framework hooks.
- **Configuration is code** — scrape jobs, data sources, dashboards all live in version control.
- **Scope is intentional** — asynchronous workers, agent metrics, log shipping, and distributed tracing are deferred as extensions, not ignored as oversights.

The result is an observability surface small enough to reason about in full, yet with clearly marked seams for every realistic extension the system will eventually need.
