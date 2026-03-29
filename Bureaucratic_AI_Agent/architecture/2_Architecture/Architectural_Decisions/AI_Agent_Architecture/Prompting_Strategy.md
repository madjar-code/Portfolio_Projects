## **1. Overview**

Prompting is the central mechanism of the AI agent's operation. It is through the prompt that the agent receives instructions, context, and constraints for processing an application.

A key feature of the system is **dynamic prompt composition**: the final prompt is assembled at runtime from the procedure, application metadata, and documents. This allows the agent to adapt to various types of procedures without changing the code.

The prompt performs several functions:

- sets the agent's role and working context,
- transmits procedure instructions,
- provides data for analysis,
- defines the output data format,
- guides the reasoning process.

---

## **2. Prompt Architecture**

The agent's prompt consists of several logical blocks, each serving its own purpose.

### **2.1 System Prompt**

Defines the agent's role and general working rules.

**Purpose:**

- setting the context ("you are a document validation expert")
- defining the working style (analytical, detail-oriented)
- setting general constraints (do not invent data, be objective)

**Characteristics:**

- static for all tasks
- sets the agent's "personality"
- defines the tone of voice

### **2.2 Procedure Instructions**

A dynamic block loaded from the Procedure Database.

**Contains:**

- procedure description
- required documents
- validation rules
- decision-making criteria
- examples of correct/incorrect applications

**Role:**

> The procedure is the agent's **runtime logic**. It defines what exactly needs to be checked and how to interpret the results.
> 

### **2.3 Application Context**

Data for a specific application.

**Includes:**

- application metadata (form_data)
- link to document in Object Storage
- document metadata (filename, format, size)

**Important:**

> The document text itself is **not included in the prompt**. The agent receives only a link and reads the document through tools (OCR, PDF parser) as needed.
> 

**Format:**

```
# Application ID: {application_id}

## Form Data:
{form_data as JSON}

## Document:
- Filename: passport_scan.pdf
- Format: PDF
- Size: 2.3 MB
- Storage URL: s3://bucket/user_123/app_456/doc.pdf

Use tools to read the document as needed.
```

### **2.4 Task Definition**

Explicit formulation of the task.

**Example:**

```
Your task:
1. Analyze the provided documents
2. Check compliance with procedure requirements
3. Extract structured data
4. Identify problems and discrepancies
5. Make a decision: ACCEPT or REJECT
6. Generate a report in the specified format
```

### **2.5 Output Format Specification**

Definition of the output data structure.

**Used:**

- JSON Schema
- Pydantic models (via structured output)
- examples of correct format

**Goal:**

- guarantee response parsability
- ensure structure consistency
- simplify result validation

---

## **3. Prompt Composition**

The final prompt is dynamically assembled by the **Prompt Builder** component.

### **3.1 Composition Pipeline**

```
1. Load System Prompt (static)
   ↓
2. Load Procedure Metadata (from SQLite)
   ↓
3. Load Procedure Instructions (from Knowledge Base file)
   ↓
4. Extract Application Metadata (from task)
   ↓
5. Add Document Metadata (filename, URL, format)
   ↓
6. Compose Final Prompt
   ↓
7. Add Output Format Schema
```

**Important:**

> The document is **not parsed in advance**. The agent receives only a link and reads it through tools as needed.
> 

### **3.2 Context Window Management**

LLM has a limited context window. The system solves this problem through **lazy document loading**.

**Key principle:**

> The document is **not loaded into the prompt entirely**. The agent receives only metadata and reads the necessary parts through tools.
> 

**Advantages:**

- **token savings** — only relevant information enters the prompt
- **flexibility** — the agent decides which parts of the document to read
- **scalability** — large documents can be processed

**Tools for working with documents:**

- `read_document_page(page_number)` — read a specific page
- `ocr_document_region(page, x, y, width, height)` — OCR for a region
- `extract_field_from_document(field_name)` — extract a specific field
- `search_in_document(query)` — find text in the document

**Monitoring:**

- tracking prompt size (in tokens)
- number of tool calls for document reading
- data extraction efficiency

### **3.3 Dynamic Content Injection**

Some parts of the prompt are added conditionally:

- **Few-shot examples** — if the procedure contains examples (from Knowledge Base)
- **Previous attempts** — if this is a retry after an error
- **Reflection notes** — if the agent is performing self-correction
- **Partial results** — if the agent has already extracted some data

## **4. Prompting Techniques**

The agent uses several techniques to improve reasoning quality.

### **4.1 Chain-of-Thought (CoT)**

The agent explicitly formulates intermediate reasoning steps.

**Implementation:**

```
Before making a decision:
1. Describe what you see in the documents
2. Compare with procedure requirements
3. Identify discrepancies
4. Draw a conclusion
```

**Advantages:**

- improves accuracy
- makes reasoning transparent
- simplifies debugging

### **4.2 ReAct (Reasoning + Acting)**

The agent alternates between reasoning and actions (tool calls).

**Cycle:**

```
Thought → Action → Observation → Thought → ...
```

**Example:**

```
Thought: "Need to extract full name from passport"
Action: extract_field(document_id="passport", field="full_name")
Observation: "Ivanov Ivan Ivanovich"
Thought: "Now need to compare with form data"
```

This pattern is implemented through the **Reasoning Loop** component (see diagram).

### **4.3 Self-Consistency**

For critical decisions, the agent can generate multiple response variants and choose the most frequent one.

**Application:**

- final ACCEPT/REJECT decision
- extraction of critical fields (dates, numbers)

**Trade-off:**

- increases latency and cost
- improves reliability

## **5. Prompt Versioning**

Prompts evolve over time. The system supports versioning.

### **5.1 Version Control**

Each procedure has a prompt version:

```sql
CREATE TABLE procedures (
    id TEXT PRIMARY KEY,
    name TEXT,
    prompt_version TEXT,  -- "v1.2.3"
    instructions TEXT,
    ...
);
```

### **5.2 A/B Testing**

New prompt versions are tested on a subset of tasks:

- 90% of tasks use the stable version
- 10% of tasks use the experimental version
- metrics are compared

### **5.3 Rollback Strategy**

If quality degrades, rollback to the previous version is possible:

- monitoring accuracy after deploying a new version
- automatic rollback when metrics drop
- manual override for critical cases

## **6. Knowledge Base and Procedure Storage**

Procedure data is stored in two places.

### **6.1 Procedure Database (SQLite)**

Stores **procedure metadata**:

```sql
CREATE TABLE procedures (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    version TEXT,
    required_document_types TEXT,  -- JSON array
    instruction_file_path TEXT,    -- Path to instruction file
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Role:**

- quick procedure search by ID
- versioning
- meta information for filtering

### **6.2 Knowledge Base (File Storage)**

Stores **full procedure instructions** as text files (Markdown).

**Structure:**

```
knowledge_base/
├── procedures/
│   ├── passport_md_v1.md
│   ├── passport_md_v2.md
│   ├── drivers_license_v1.md
│   └── ...
└── examples/
    ├── passport_md_examples.md
    └── ...
```

**Procedure file contents:**

```markdown
# Procedure: Passport MD Application

## Description
...

## Required Documents
...

## Validation Rules
...

## Agent Prompt
...

## Examples
### Example 1: Correct Application
...

### Example 2: Typical Error
...
```

### **6.3 Loading Process**

When receiving a task:

```
1. Agent receives procedure_id from the task
   ↓
2. Loads metadata from SQLite
   ↓
3. Reads instruction file from Knowledge Base
   ↓
4. Includes instructions in the prompt
```

### **6.4 Example Types in Knowledge Base**

- **Positive examples** — correct applications
- **Negative examples** — typical errors
- **Edge cases** — complex boundary cases
- **Clarifications** — explanations for ambiguous rules

Examples are included in the prompt as **few-shot learning** to improve the agent's performance quality.

## **7. Summary**

Prompting in the system is not static text, but a **dynamic context composition process**.

Key principles:

- **modularity** — the prompt is assembled from independent blocks
- **adaptability** — content depends on the procedure and data
- **lazy loading** — documents are read through tools, not included in the prompt
- **versioning** — prompts evolve and are tested
- **transparency** — the reasoning process is explicitly formulated
- **efficiency** — minimization of context window usage

**Storage architecture:**

- **SQLite** — procedure metadata (quick search)
- **Knowledge Base** — full procedure instructions (files)
- **Object Storage** — user documents (read on demand)

The Prompt Builder (see diagram) is responsible for all composition logic and is a critical component of the system.