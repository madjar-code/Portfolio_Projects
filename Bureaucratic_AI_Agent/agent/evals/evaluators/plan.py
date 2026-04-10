from core.agent_executor import TraceEvent
from evals.schemas import EvalCase


def evaluate_plan(case: EvalCase, trace: list[TraceEvent]) -> tuple[float, list[str]]:
    """
    Returns (plan_score, violations).

    Checks two things:
    1. Presence — all tools in plan_steps_must_complete were called at least once.
    2. Order — consecutive tools in the list were called in that relative order.

    Score = (total_checks - violations) / total_checks
    Total checks = len(steps) presence + (len(steps) - 1) order pairs.
    """
    if not case.plan_steps_must_complete:
        return 1.0, []

    # Only action-step tool calls (not reflection side-calls), preserving order
    ordered_calls = [
        e.tool_name for e in trace
        if e.step == "action" and e.tool_name and e.tool_name != "submit_report"
    ]

    steps = case.plan_steps_must_complete
    violations: list[str] = []

    # 1. Presence check
    for tool in steps:
        if tool not in ordered_calls:
            violations.append(f"required tool not called: {tool}")

    # 2. Order check — each consecutive pair must appear in order
    for i in range(len(steps) - 1):
        first, second = steps[i], steps[i + 1]
        if first in ordered_calls and second in ordered_calls:
            if ordered_calls.index(second) < ordered_calls.index(first):
                violations.append(f"order violation: '{second}' called before '{first}'")

    total = len(steps) + max(0, len(steps) - 1)
    score = (total - len(violations)) / total
    return round(score, 3), violations
