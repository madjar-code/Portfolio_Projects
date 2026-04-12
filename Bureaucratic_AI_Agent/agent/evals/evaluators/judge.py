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

The agent's decision is either ACCEPT or REJECT. Use only the section that matches.

---

### If decision == ACCEPT

**issues_score**
- 1.0: issues_found is empty or absent. Correct — a valid application has no issues.
- 0.0: issues_found contains items. The agent invented problems that do not exist.

**recommendations_score**
- 1.0: recommendations is null, absent, or a brief positive confirmation.
- 0.5: recommendations exist but are neutral / do not contradict the decision.
- 0.0: recommendations describe problems or ask the applicant to fix something.

---

### If decision == REJECT

**issues_score**
- 1.0: All real problems are listed, attributed to the correct fields, severity is appropriate.
- 0.5: Some problems found but list is incomplete or fields are mislabeled.
- 0.0: issues_found is empty, or the listed issues are entirely wrong.

**recommendations_score**
- 1.0: Actionable and specific — tells the applicant exactly what to fix.
- 0.5: Vague but relevant to the actual problems.
- 0.0: Missing, irrelevant, or contradicts the REJECT decision.

---

### reasoning_score (applies to both ACCEPT and REJECT)
- 1.0: The trace reasoning covers all validated fields; conclusions match tool results; confidence is calibrated.
- 0.5: Reasoning present but with gaps or unexplained jumps.
- 0.0: No meaningful reasoning, or reasoning contradicts the final report.
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
