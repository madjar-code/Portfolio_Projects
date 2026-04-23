## **1. Overview**

Reliability is the property that **a submitted request eventually reaches a terminal state**, even when individual components fail. Failure is treated as the normal case — every boundary in the system assumes its counterpart can be slow, broken, or temporarily absent.

The design rests on three ideas:

- **Layered retries.** Each boundary (transport, LLM, callback, task publish) handles its own failures locally, with policies tuned to its cost profile.
- **Bounded recovery.** No retry loop is infinite. Every layer has an explicit exit — success, terminal failure, or dead-letter — so no request can stall silently.
- **Terminal honesty.** When recovery fails, the system says so. A stuck state is worse than an acknowledged failure.

**Principle:**

> Reliability is not "no failures ever". It is "every failure has a defined outcome within a bounded time."

---

## **2. Failure Classes**

The system distinguishes **transient** failures — retrying will likely succeed — from **terminal** failures — retrying will only waste resources.

- **Transient:** connection resets, timeouts, rate limits, 5xx responses, broker blips, provider hiccups.
- **Terminal:** malformed input, authentication errors, 4xx client errors, semantically invalid documents.

Retry policies only apply to transient failures. Terminal failures short-circuit to the final state immediately — masking them behind retries wastes resources and hides real bugs.

**Principle:**

> The retry budget is for problems the network caused. Bugs deserve visibility, not backoff.

---

## **3. Layered Retry Strategy**

Each integration point has its own retry layer. None of them knows about the others — composition is implicit through their individual guarantees.

### **3.1 Transport Layer (Message Queue)**

The task queue is durable, and deliveries are acknowledged only on success. A failed handler re-queues the message for redelivery. This is what guarantees that a request once enqueued is eventually processed, regardless of what happens to the consumer.

But redelivery alone is not enough: a genuinely poisonous message can loop forever. The queue is configured with a **redelivery limit**; once exceeded, the message is routed to a **Dead Letter Queue** (see §5) instead of being requeued again.

### **3.2 LLM Layer (Model Fallback Chain)**

The agent maintains an **ordered list of usable models**. A reasoning call starts with the primary and, on transport failure (rate limit, timeout, 5xx, connection error), falls back to the next model in the list.

Fallback triggers only on transport failures; logical failures (invalid auth, bad request) are surfaced immediately. The chain is finite — if every model in the list fails, the agent's task fails.

**Principle:**

> A single LLM provider is a single point of failure. A fallback chain turns one fragile dependency into a graceful degradation step.

### **3.3 Callback Layer**

After the agent produces a report, it must deliver it back to the Backend. The delivery channel is an independent retry layer, separate from the agent's own execution:

- bounded number of attempts with exponential backoff
- distinguishes retryable transport errors from non-retryable 4xx responses
- on exhaustion, raises — which promotes the failure to the transport layer (and eventually to the DLQ)

**Why this is its own layer:**

> Running the agent again because the Backend had a momentary 5xx would waste far more resources than just retrying the HTTP call. Callback retry is cheap; LLM re-execution is not.

### **3.4 Task Publish Layer**

Publishing a task happens in two places, with different policies:

- **Inside the API request** — synchronous publish to the worker queue. A blocking retry would keep the user waiting, so this path fails fast: the application is marked terminal and the caller gets a `5xx` immediately.
- **Inside the worker** — asynchronous publish to the agent queue. No user is watching; this path retries with bounded exponential backoff and, on exhaustion, transitions the application to the terminal failure state.

**Principle:**

> Retry where the user is not watching; fail fast where they are.

---

## **4. Timeouts**

Retries are only meaningful against a bounded clock. The system enforces timeouts at three scales:

- **Per-LLM call** — a single model invocation cannot hang indefinitely; it fails and the fallback chain advances.
- **Per-callback attempt** — a single HTTP POST has a bounded deadline; its failure triggers the next retry attempt.
- **Whole-task** — the agent's total work on a single task is capped. Exceeding the cap is itself a transport failure, which triggers the redelivery/DLQ path.

**Principle:**

> Every wait has an exit. Without total-task timeouts, a single hung request can hold a worker slot forever and starve the queue.

---

## **5. Dead Letter Queue**

The DLQ is the system's **terminal drain** for requests that cannot be processed within the retry budget. It is a normal queue with no active consumer.

**What goes there:**

- messages whose redelivery limit has been exhausted,
- messages that failed parsing (structural corruption — no retry can help),
- messages whose total-task timeout was exceeded repeatedly.

**What doesn't:**

- transient failures still within their retry budget,
- tasks currently being retried at a higher layer (LLM fallback, callback retry).

**Purpose:**

- **Isolation** — a poisonous message cannot starve the main queue.
- **Preservation** — the full message body and delivery history remain available for post-mortem.
- **Operator leverage** — a human can inspect, replay (back into the main queue) or drop deliberately, once the underlying cause is fixed.

**Principle:**

> A message in DLQ is a question for a human, not a retry for the system. The DLQ is the line between automated recovery and operator intervention.

---

## **6. Terminal States**

An application's lifecycle has explicit terminal states, and reliability failures map onto them honestly:

- A decision arriving through a successful callback → the decision's target state (`APPROVED` / `REJECTED`).
- The agent reporting an internal error → `FAILED`.
- All retry layers exhausting without delivering a report → `FAILED`.
- The task layer failing to enqueue in the first place → `FAILED`.

The reason is recorded alongside the status. `FAILED` does not mean "the agent rejected the application" — it means "the system could not produce a verdict within its reliability budget". These are different outcomes and must be distinguishable in the UI, in logs, and in metrics.

---

## **7. Observability of Failures**

Reliability without visibility decays into cargo-cult retries. Every retry decision is logged with enough context to answer three questions after the fact:

- **What failed?** (error class, upstream component)
- **How many attempts?** (retry counter, attempt timestamps)
- **Where did it end?** (success, next fallback, DLQ, terminal failure)

Structured log lines at each layer make these visible in the normal log pipeline. No dedicated error-reporting integration is introduced for this iteration — the log stream is the source of truth.

---

## **8. Scope and Non-Goals**

The design keeps the scope narrow on purpose. The following are **intentionally deferred**, not forgotten:

- **Idempotency on the agent side.** Today a redelivered message may re-run the LLM. Callback itself is idempotent on the Backend (`update_or_create`), so no data corruption results — only duplicated work. Persistent agent-side report storage would close this gap but adds state to an otherwise stateless process.
- **Circuit breaker around the LLM providers.** The fallback chain is enough for normal flakiness. A circuit breaker becomes useful only when a provider is down long enough that fast-failing the whole chain is preferable to trying each model in turn.
- **Automated DLQ replay tooling.** For now, replay is a manual operation via the broker's management UI. An automated replay endpoint can be added once there is real DLQ traffic to justify it.
- **Cross-service distributed tracing.** Correlation today is the `X-Request-Id` header in logs. Upgrading to span-based tracing is orthogonal to reliability and handled under the observability track.

Each omission is a **seam**: the current architecture admits it without structural change when the need is concrete.

---

## **9. Failure Scenario Reference**

The sections above describe principles; this section pins them down to concrete outcomes. Each scenario lists: what triggered it, how the system reacts, where the request ends up, and what status the application carries at each moment.

This is intentionally the most specific section of the document — reliability guarantees are only meaningful when observable outcomes are nailed down.

**Deployment assumption:** the scenarios below assume **one agent instance and one Celery worker**. Reliability here is guaranteed by *message preservation and recovery after restart*, not by parallel fail-over. An extended outage of the sole worker means the queue pauses; messages wait until the worker returns. Horizontal scaling is a separate concern, orthogonal to reliability.

### **9.1 Task Publish (Backend → queue)**

The user has just submitted the application; the task has to reach the worker queue, and then the agent queue.

| Scenario | Reaction | Final outcome | Application status |
|---|---|---|---|
| Broker unreachable at the moment of submit (sync publish) | View catches `OperationalError`, returns `503` to caller, marks application terminal | Task never enters worker queue; operator sees an infrastructure incident in logs | `SUBMITTED` → `FAILED` in one step |
| Broker briefly unavailable during worker-side publish, recovers in < retry budget | Worker retries with exponential backoff | Normal flow resumes | Stays `PROCESSING` |
| Broker unavailable through all worker retries | Task fails; `on_failure` hook marks the application terminal | No task reaches the agent queue | `PROCESSING` → `FAILED` |
| Worker crashes mid-publish | Task not acked; on worker restart, broker redelivers it | Worker retries publish after restart | Stays `PROCESSING` while worker is down |

### **9.2 Queue Delivery (agent side)**

The task is in `agent_tasks`; the agent consumer is responsible for processing it.

| Scenario | Reaction | Final outcome | Application status |
|---|---|---|---|
| Agent container dies mid-processing | Message not acked; stays in queue. Agent restarts → consumer re-subscribes → picks up the waiting message | Processing resumes from scratch for that message | Stays `PROCESSING`; no user-visible change |
| Consumer network flake | Robust-connect reconnects automatically; subscription restored | Delivery continues | `PROCESSING` |
| Message body is malformed JSON | Parser raises → explicit reject without requeue | Routed to DLQ for operator inspection | `PROCESSING` until whole-task timeout or operator action → `FAILED` |
| Schema-invalid payload | Same as malformed JSON | DLQ | Same |
| Same message fails N consecutive times | `x-death` count ≥ N → reject without requeue | DLQ (infinite loop broken) | `PROCESSING` → operator intervenes |

### **9.3 LLM Calls**

Each model invocation inside the reasoning loop.

| Scenario | Reaction | Final outcome | Application status |
|---|---|---|---|
| Primary model rate-limited (429) | Fallback chain advances to next model | Agent continues | `PROCESSING` |
| Primary model 5xx / timeout / connection error | Fallback advances | Agent continues | `PROCESSING` |
| Per-LLM timeout exceeded | Treated as transient failure → fallback advances | Agent continues | `PROCESSING` |
| All models in the chain fail transiently | Chain exhausted → task raises | Queue requeues → DLQ after redelivery limit | `PROCESSING` → operator intervenes |
| Auth failure (401/403) | **Not retried**, **no fallback** — surfaces as bug | Task raises → queue retry → DLQ | `PROCESSING` → operator |
| Bad request (400) | Same as auth — surfaces | Same | Same |

### **9.4 Agent Execution Envelope**

The full run of the reasoning loop for one task.

| Scenario | Reaction | Final outcome | Application status |
|---|---|---|---|
| Agent finishes normally, decision = `ACCEPT` | Report generated → callback | — | `APPROVED` (set by callback) |
| Agent finishes normally, decision = `REJECT` | Report → callback | — | `REJECTED` |
| Agent finishes, decision = `ERROR` | Report → callback | — | `FAILED` |
| Agent exceeds `max_iterations` | Produces an `ERROR` report as fallback | Report → callback | `FAILED` |
| Whole-task timeout exceeded | Raises → message returned to queue | DLQ after redelivery limit | `PROCESSING` → operator |
| Uncaught exception in agent code | Raises → requeued | DLQ after redelivery limit | Same |

### **9.5 Callback Delivery (Agent → Backend)**

The report is already produced; only the HTTP hop remains.

| Scenario | Reaction | Final outcome | Application status |
|---|---|---|---|
| Backend briefly 5xx or times out | Bounded retry with exponential backoff | Delivered on a later attempt | Set by callback on success |
| Network error mid-callback | Retryable; treated as transient | Retries | Same |
| Backend down for all callback retries | Attempts exhausted → task raises → message requeued | DLQ after redelivery limit; **report body remains inside the DLQ message** for replay | `PROCESSING` until operator replays |
| Backend returns 4xx (bad signature, malformed body) | **Not retried** — surfaces as bug | Task raises → queue retry → DLQ | `PROCESSING` → operator |
| Backend returns 404 (application not found) | Same — structural bug, not transient | DLQ | Same |

### **9.6 How the Application Reaches `FAILED`**

`FAILED` is the terminal state for any reliability outcome that is not a decision. There are three distinct paths to it, and each should be logged with its cause:

| Path to `FAILED` | Where the state is written |
|---|---|
| Broker unreachable at submit time (sync publish) | API view (on `OperationalError` from `.delay()`) |
| Broker unavailable through worker publish retries | Worker `on_failure` hook |
| Agent explicitly returns `decision = ERROR` | Callback handler (via the decision mapping) |
| DLQ inspection — operator moves a stuck request to `FAILED` manually | Operator tooling (out of scope of this iteration) |

Every `FAILED` should be accompanied by a reason code in logs — `enqueue_failed`, `publish_exhausted`, `agent_error`, `dlq_finalized` — so that operators can distinguish them without reading the trace.

### **9.7 Non-Scenarios (what deliberately is not a failure)**

Some conditions look like failures but are part of normal flow:

- **Consumer disconnect and automatic reconnect** — not a failure as long as the message stays unacked on the broker. Reliability is preserved by design.
- **A model in the fallback chain returning a valid but "low-quality" answer** — quality evaluation is the job of the evaluation pipeline, not the reliability layer.
- **A callback arriving late because of a retry** — this is a success from the reliability point of view. Latency impact belongs to the SLOs, not the retry policy.

---

## **10. Summary**

- **Reliability = every failure has a bounded outcome.** No infinite loops, no silent drops, no stuck states.
- **Layered retries, not one big loop.** Each boundary handles its own failures with a policy matching its cost.
- **Transient vs. terminal is a first-class distinction.** Only transient failures are retried; terminal failures are surfaced immediately.
- **Bounded by time and count at every layer.** Per-call timeouts, whole-task timeouts, capped retry attempts.
- **A Dead Letter Queue is the terminal drain.** Anything the system cannot recover from lands there for operator inspection.
- **Terminal states are honest.** `FAILED` is a reliability outcome, distinct from a rejection decision — and users see it as such.
- **Logs are the reliability source of truth.** Every retry decision leaves a structured trace; no separate error-reporting integration is required for this iteration.

This keeps the system resilient to ordinary operational failures — broker blips, provider outages, brief downstream errors — without adding ceremony the project does not yet need.
