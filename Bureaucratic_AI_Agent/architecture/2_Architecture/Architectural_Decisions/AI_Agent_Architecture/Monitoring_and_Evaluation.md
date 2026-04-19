## **1. Overview**

Monitoring and evaluation are two complementary feedback loops that keep the agent trustworthy over time.

- **Monitoring** operates on **live traffic**. It answers: *what is happening right now?* — which procedures are being processed, what decisions the agent is making, where it fails, how long a reasoning loop takes.
- **Evaluation** operates on **curated datasets** offline. It answers: *is the agent still good enough to ship?* — every change to the prompt, the model, or a tool is scored against known-good examples before reaching production.

Neither replaces the other. Monitoring catches real-world problems after release; evaluation prevents obvious regressions before release.

---

## **2. Runtime Observability**

The agent exposes its internal state through three independent channels.

### **2.1 LangFuse — per-run tracing**

Every agent run is a single **trace** in LangFuse, keyed by `application_id`. Inside the trace we record:

- **generations** — each LLM call (model, input messages, output, tokens, latency)
- **events** — each tool invocation (name, args, result)
- **metadata** — procedure, prompt version, final decision, iteration count

**Role:**

> LangFuse is the **narrative view** of a run. It lets a reviewer reconstruct *why* the agent decided ACCEPT or REJECT for a specific application.

If LangFuse is unavailable or not configured, observability degrades to a no-op wrapper — the agent keeps working, just without the trace.

### **2.2 Structured Logging**

The agent writes to two sinks:

- **stdout** — for Docker / orchestrator log capture
- **`agent.log`** — a local rotating file (10 MB × 5 files), useful for `grep` and for preserving the last few hours of activity without a backend.

Log records are line-oriented and include the application id where relevant, so a single run can be reconstructed with a plain text search even if LangFuse is disabled.

### **2.3 Error Reporting (Sentry)**

Uncaught exceptions and agent-level failures are reported to Sentry (production only). Sentry groups similar errors and surfaces regressions that otherwise hide inside long successful batches.

### **2.4 What the agent deliberately does not monitor**

- **Per-user PII** is not attached to spans or log lines.
- **Document contents** are not copied into traces; only metadata (filename, format) is recorded. The full text exists transiently during tool calls.

These constraints keep observability useful without turning it into an audit liability.

---

## **3. Offline Evaluation**

Evaluation runs **outside** the live pipeline. It loads a fixed dataset, executes the agent against each case, and scores the outputs through evaluators.

### **3.1 Dataset Organization**

Datasets live under `agent/evals/dataset/` and are **split along two axes**:

- **By procedure type** — separate dataset per procedure. A change to the `passport_md_strict` prompt only needs to be re-scored against its own dataset, not the whole corpus.
- **By purpose** — for each procedure, a **functional** dataset (does the agent make the right decision on realistic inputs?) is kept separate from a **security** dataset (does the agent resist prompt injection, instruction override, data exfiltration attempts?).

```
agent/evals/dataset/
├── business_reg.json
├── lease_agreement_md.json
├── lease_agreement_md_security.json
├── passport_md_strict.json
└── passport_md_strict_security.json
```

**Why the split matters:**

> A functional dataset measures *accuracy*. A security dataset measures *robustness*. These two have different cost profiles, different baselines, and often different owners — merging them would hide regressions in one behind gains in the other.

### **3.2 Evaluators**

Each case is scored along multiple dimensions rather than reduced to a single pass/fail.

- **Decision evaluator (LLM-as-judge)** — compares the agent's final decision and rationale against the expected outcome.
- **Plan evaluator** — checks that the agent's reasoning plan covered the steps required by the procedure.
- **Tool-usage evaluator** — checks that expected tools were called and unnecessary ones were avoided.

**Principle:**

> A run can pass the decision evaluator while still failing the plan or tool evaluator (for example, arriving at the right answer through the wrong path). Surfacing those separately is what makes evaluation actionable rather than just a green/red badge.

### **3.3 Fixtures**

Realistic inputs used by datasets (sample PDFs, form data, expected outputs) live under `agent/evals/fixtures/`. They are checked into the repo so evaluation runs are reproducible and diffable over time.

---

## **4. How the two feedback loops connect**

```
   ┌─────────────────┐        regression found        ┌─────────────────┐
   │  Live Agent     │ ──────────────────────────▶    │  Evaluation     │
   │ (LangFuse,      │                                │  dataset update │
   │  logs, Sentry)  │ ◀──────────────────────────    │ (+ new case)    │
   └─────────────────┘     new prompt version          └─────────────────┘
```

- A failure in production → a new case is distilled from the LangFuse trace and added to the relevant dataset.
- A new prompt / model / tool → evaluation scores must not drop before the change is merged.

Over time this turns real incidents into permanent guardrails.

---

## **5. Summary**

The system treats monitoring and evaluation as two independent **feedback mechanisms** with distinct roles:

- **Monitoring** — live, per-run, narrative-oriented. Answers "what happened".
  - LangFuse traces, rotating `agent.log`, Sentry.
- **Evaluation** — offline, dataset-driven, regression-oriented. Answers "did we get worse".
  - Datasets split by procedure and by purpose (functional vs security).
  - Multiple evaluators (decision, plan, tool-usage) score each case along separate axes.

**Key principles:**

- **Separation of concerns** — monitoring does not replace evaluation, and vice versa.
- **Fail-open observability** — if LangFuse or Sentry is unavailable, the agent still runs; traces are best-effort.
- **Security is a first-class dataset** — not an afterthought bolted onto functional suites.
- **Incidents become test cases** — real failures feed back into the offline dataset.

This separation ensures the agent can be both **debugged in production** and **improved in a controlled way** without relying on one channel for both jobs.
