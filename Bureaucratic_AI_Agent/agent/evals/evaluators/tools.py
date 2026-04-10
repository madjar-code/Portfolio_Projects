from core.agent_executor import TraceEvent
from evals.schemas import EvalCase, DeterministicResult


def evaluate_tools(case: EvalCase, trace: list[TraceEvent]) -> DeterministicResult:
    called = {e.tool_name for e in trace if e.tool_name}
    violations: list[str] = []

    for tool in case.required_tools:
        if tool not in called:
            violations.append(f"required tool not called: {tool}")

    for tool in case.forbidden_tools:
        if tool in called:
            violations.append(f"forbidden tool was called: {tool}")

    total = len(case.required_tools) + len(case.forbidden_tools)
    score = (total - len(violations)) / total if total > 0 else 1.0

    return DeterministicResult(
        decision_correct=False,  # filled by caller
        plan_score=0.0,          # filled by PlanEvaluator
        tool_score=round(score, 3),
        tool_violations=violations,
    )
