## **1. Overview**

Task processing by the agent is an **iterative cycle** of planning, execution, and reflection.

The agent does not follow a rigid algorithm. Instead, it:

- receives procedure instructions through the prompt,
- forms an action plan,
- executes the plan through tools,
- reflects on the results,
- adjusts actions as necessary.

The key feature is that the agent **interprets** the procedure and **adapts** its actions based on the data.

Main components (see diagram):

- **Agent Orchestration** — manages the overall flow
- **Prompt Builder** — forms the context with instructions
- **Reasoning Loop** — iterative cycle of "plan → action → reflection"
- **Tool Set** — tools for working with documents and data
- **LLM Registry** — manages LLM calls

## **2. High-Level Execution Flow**

Task processing goes through three main phases.

### **2.1 Initialization**

```
1. Queue Consumer receives a task from the queue
   ↓
2. Agent Orchestration initializes the context
   ↓
3. The procedure is loaded (metadata from SQLite + instructions from Knowledge Base)
   ↓
4. Prompt Builder forms the prompt with:
   - procedure instructions
   - application metadata (form_data)
   - document metadata (URL, filename)
   - list of available tools
```

**Result:** the agent receives the full context to begin work.

### **2.2 Execution (Reasoning Loop)**

The agent performs the task through an **iterative cycle**:

```
loop until task_complete:
    Planning: forming/adjusting the plan
    ↓
    Action: selecting and calling a tool
    ↓
    Observation: receiving the result
    ↓
    Reflection: analyzing progress and adjusting
```

**Important:**

> The agent **does not follow a rigid plan**. It adapts its actions based on the received data.
> 

### **2.3 Completion**

When the agent has completed processing:

```
1. Forming a structured report (AIReport)
   ↓
2. Validating the report format (Pydantic)
   ↓
3. Sending via Callback Client to Backend API
   ↓
4. Logging the result
   ↓
5. Task completion
```

## **3. Reasoning Loop**

This is the **central mechanism** of the agent. Implemented through LangGraph state machine.

### **3.1 Loop Structure**

### **3.2 Planning**

The agent forms or adjusts the plan based on:

- procedure instructions (from the prompt),
- current execution state,
- already collected data.

**Example of an initial plan:**

```
Passport application processing plan:
1. Read the first page of the document (birth certificate)
2. Extract full name via OCR
3. Extract date of birth
4. Compare with form data
5. Check in Civil Registry database via external API
6. Make decision: ACCEPT or REJECT
```

**Important:**

> The plan **is not fixed**. The agent adjusts it when problems are detected or unexpected data is received.
> 

### **3.3 Action (Tool Execution)**

The agent selects and executes a tool from the Tool Set.

**Available tools:**

- `read_document_page(page_number)` — read a document page
- `ocr_document_region(page, x, y, width, height)` — OCR for a region
- `extract_field_from_document(field_name)` — extract a specific field
- `call_external_api(endpoint, params)` — request to external API
- `search_knowledge_base(query)` — search for examples

**Example:**

```json
Action: read_document_page
Parameters: {"page_number": 1}

Result: "BIRTH CERTIFICATE\nFull Name: Ivanov Ivan Ivanovich\n..."
```

### **3.4 Observation**

The agent receives the tool execution result and adds it to the context.

```
Observation:
First page of the document has been read.
Text found: "Full Name: Ivanov Ivan Ivanovich"
```

### **3.5 Reflection**

The agent analyzes the results and decides on further actions.

**Reflection questions:**

- Has the goal of the current step been achieved?
- Is plan adjustment needed?
- Have any discrepancies or problems been detected?
- Is there enough data to make a final decision?

**Example reflection:**

```
Reflection:
- Full name successfully extracted: "Ivanov Ivan Ivanovich"
- Matches form data: "Ivanov Ivan Ivanovich" ✓
- Next step: extract date of birth
```

**Reflection result:**

- **Continue** → return to Planning for the next step
- **Complete** → proceed to report formation

## **4. Adaptive Planning**

A key feature of the agent is its ability to **adjust the plan** during execution **within the procedure instructions**.

### **4.1 Initial Planning**

When receiving a task, the agent forms an initial plan based on the procedure instructions from the prompt.

### **4.2 Bounded Adaptation**

The agent adapts its actions, **but remains within the procedure boundaries**.

**Important principle:**

> The agent can change the **method** of executing steps, but cannot ignore the **procedure requirements**.
> 

**What the agent CAN do:**

- choose an alternative tool (OCR instead of PDF parser)
- repeat an action with different parameters
- use a different approach to data extraction

**What the agent CANNOT do:**

- skip a mandatory check
- change procedure requirements
- search for data where the procedure does not expect it

### **4.3 Replanning Example**

**Scenario 1: Permissible adaptation**

```
Procedure instruction: "Extract full name from birth certificate"

Original plan:
1. Read document via PDF parser
2. Find full name

Problem: PDF parser could not extract text

Plan adjustment (permissible):
1. Use OCR to read the document
2. Find full name
3. If OCR doesn't help — mark document as unreadable
```

**Scenario 2: Impermissible adaptation**

```
Procedure instruction: "Full name must be on the first page of the certificate"

Original plan:
1. Read the first page
2. Extract full name

Problem: No full name on the first page

Impermissible adjustment:
❌ Read the second page and search there

Permissible adjustment:
✓ Use OCR for the first page (different reading method)
✓ If not found — record as NON-COMPLIANCE with requirements
✓ Include in report: "Full name is missing on the first page"
```

### **4.4 Handling Non-Compliance**

If data does not meet procedure requirements:

```
1. The agent does NOT try to "fit" data to requirements
2. Records the discrepancy in the report
3. Marks as issue with severity: "critical"
4. Recommends: REJECT
```

**Result:**

> The agent adapts to **technical problems** (how to read the document), but strictly follows **business requirements** (what should be in the document).
> 

## **5. Reflection and Self-Correction**

The agent is capable of **analyzing its actions** and correcting errors.

### **5.1 Reflection Levels**

**Lightweight Reflection** — after each action:

- What was received?
- Does it meet expectations?
- Are additional actions needed?

**Deep Reflection** — before the final decision:

- Have all checks been completed?
- Are there any contradictions in the data?
- Is there sufficient confidence to make a decision?

### **5.2 Self-Correction Example**

```
Observation:
Date extracted: "01.13.1990"

Reflection:
This is an invalid date (month cannot be 13).
Probably, the format is MM.DD.YYYY, not DD.MM.YYYY.

Correction:
Reinterpret as "13.01.1990" (DD.MM.YYYY).
Result: "1990-01-13"
```

### **5.3 Confidence Assessment**

The agent evaluates confidence in its conclusions:

```json
{
  "field": "birth_date",
  "value": "1990-01-13",
  "confidence": 0.85,
  "reasoning": "Date extracted from clear text, but format required interpretation"
}
```

With low confidence (< 0.7), the agent:

- marks the field as requiring verification,
- includes a warning in the report,
- may attempt an alternative approach.

## **6. Error Handling and Retry**

The system handles errors at multiple levels.

### **6.1 Tool-Level Retry**

If a tool returns an error (timeout, network error):

```
Attempt 1: read_document_page → timeout
Attempt 2: read_document_page (increased timeout) → success
```

**Parameters:**

- max retries: 3
- exponential backoff: 1s, 2s, 4s

### **6.2 LLM-Level Retry**

If LLM returns an invalid response:

```
Attempt 1: LLM → invalid JSON
Attempt 2: LLM (refined prompt + example) → valid JSON
```

### **6.3 Task-Level Retry**

If the task completely fails:

```
Attempt 1: agent execution → exception
Attempt 2: agent execution (with logs from previous attempt) → success
```

**Management:** Celery retry mechanism (max 3 attempts)

### **6.4 Graceful Degradation**

If a non-critical step fails, the agent continues working:

```
Problem: external API is unavailable

Solution:
- mark the check as "not completed"
- continue with other checks
- include a warning in the report
```

## **7. Summary**

The agent's execution cycle is an **adaptive iterative process within the procedure**, not a rigid algorithm.

**Key principles:**

- **Interpretation** — the agent receives instructions through the prompt and interprets them
- **Planning** — forms a plan based on the procedure
- **Iterativity** — cycle of "plan → action → observation → reflection"
- **Bounded Adaptation** — adjusts the **method** of execution, but not the **procedure requirements**
- **Reflection** — analyzes results and corrects errors
- **Resilience** — multi-level retry strategy
- **Lazy loading** — reads documents as needed, not entirely

**Important limitation:**

> The agent adapts to technical problems (how to read the document), but strictly follows business requirements of the procedure (what should be in the document).
> 

**Architectural components (see diagram):**

- **Agent Orchestration** — manages the overall flow
- **Prompt Builder** — forms the context with instructions
- **Reasoning Loop** — implements the iterative cycle
- **Tool Set** — provides tools for working with documents
- **LLM Registry** — manages LLM calls

This architecture ensures flexibility in execution while strictly adhering to procedure requirements.