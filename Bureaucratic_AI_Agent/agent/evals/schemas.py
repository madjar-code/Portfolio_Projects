from dataclasses import dataclass, field


@dataclass
class EvalCase:
    case_id: str
    description: str
    procedure: str
    form_data: dict
    document_url: str | None
    expected_decision: str              # "ACCEPT" | "REJECT"
    expected_issues: list[str]          # field names that should appear in issues_found
    required_tools: list[str]           # must be called at least once
    forbidden_tools: list[str]          # must not be called at all
    plan_steps_must_complete: list[int] # iteration numbers that must have tool calls


@dataclass
class DeterministicResult:
    decision_correct: bool
    plan_score: float                   # 0.0–1.0
    tool_score: float                   # 0.0–1.0
    plan_violations: list[str] = field(default_factory=list)
    tool_violations: list[str] = field(default_factory=list)


@dataclass
class JudgeResult:
    issues_score: float                 # 0.0–1.0
    recommendations_score: float        # 0.0–1.0
    reasoning_score: float              # 0.0–1.0
    judge_score: float                  # mean of above
    judge_reasoning: str


@dataclass
class EvalResult:
    case_id: str
    description: str
    expected_decision: str
    actual_decision: str | None
    deterministic: DeterministicResult
    judge: JudgeResult
    processing_time_seconds: int


@dataclass
class EvalRunSummary:
    procedure: str
    prompt_version: str
    model: str
    timestamp: str
    total_cases: int
    accuracy: float
    mean_plan_score: float
    mean_tool_score: float
    mean_judge_score: float
    results: list[EvalResult] = field(default_factory=list)
