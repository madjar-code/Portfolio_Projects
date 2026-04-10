import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import settings
from core.agent_executor import TraceEvent
from evals.schemas import EvalCase, JudgeResult

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are an impartial evaluator of an AI bureaucratic agent.\n"
    "Score the agent's output on 3 dimensions (each 0.0–1.0).\n"
    "Do NOT re-evaluate the business decision (ACCEPT/REJECT) — only score reasoning quality.\n\n"
    "Respond with valid JSON only:\n"
    '{"issues_score": 0.0, "recommendations_score": 0.0, "reasoning_score": 0.0, "reasoning": "..."}'
)

_RUBRIC = """
## Scoring rubric

### issues_score
For REJECT decisions:
- 1.0: All real issues are found, attributed to the correct fields, severity is appropriate.
- 0.5: Some issues found but incomplete or mislabeled.
- 0.0: No issues found when there clearly are some, or completely wrong fields cited.
For ACCEPT decisions:
- 1.0: issues_found is empty, which is correct — no issues means no issues.
- 0.0: issues_found is non-empty when the application is valid.

### recommendations_score
For REJECT decisions:
- 1.0: Actionable, specific, references the actual problems found.
- 0.5: Vague but relevant.
- 0.0: Missing, irrelevant, or contradicts the decision.
For ACCEPT decisions:
- 1.0: recommendations is null or absent — no correction needed for a valid application.
- 0.0: recommendations contradict the ACCEPT decision.

### reasoning_score
- 1.0: Reflection accurately summarises all validated fields; confidence is calibrated.
- 0.5: Some reasoning present but with gaps or overconfidence.
- 0.0: No meaningful reasoning, or reasoning contradicts the report.
"""


def _abbreviate_trace(trace: list[TraceEvent]) -> str:
    lines = []
    for e in trace:
        if e.step == "observation" and e.result:
            lines.append(f"[iter {e.iteration+1}] tool:{e.tool_name} → {e.result}")
        elif e.step == "reflection" and e.result:
            lines.append(f"[iter {e.iteration+1}] reasoning: {e.result}")
    return "\n".join(lines) or "(no tool calls or reasoning)"


async def evaluate_judge(
    case: EvalCase,
    procedure_text: str,
    trace: list[TraceEvent],
    submit_args: dict,
    model_name: str,
) -> JudgeResult:
    trace_text = _abbreviate_trace(trace)
    report_text = json.dumps(submit_args, indent=2, ensure_ascii=False)

    user_msg = (
        f"## Procedure instructions\n{procedure_text}\n\n"
        f"## Conversation trace (abbreviated)\n{trace_text}\n\n"
        f"## Final report submitted by agent\n```json\n{report_text}\n```\n\n"
        f"{_RUBRIC}"
    )

    model = ChatOpenAI(model=model_name, temperature=0, api_key=settings.openai_api_key)
    response = await model.ainvoke([SystemMessage(_SYSTEM), HumanMessage(user_msg)])

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        data = json.loads(content)
        issues = float(data.get("issues_score", 0))
        recs   = float(data.get("recommendations_score", 0))
        reason = float(data.get("reasoning_score", 0))
        return JudgeResult(
            issues_score=issues,
            recommendations_score=recs,
            reasoning_score=reason,
            judge_score=round((issues + recs + reason) / 3, 3),
            judge_reasoning=data.get("reasoning", ""),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Judge response parse error: %s — raw: %s", exc, response.content[:300])
        return JudgeResult(
            issues_score=0.0,
            recommendations_score=0.0,
            reasoning_score=0.0,
            judge_score=0.0,
            judge_reasoning=f"Parse error: {exc}",
        )
