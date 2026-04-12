import argparse
import asyncio
import json
import logging
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from core.agent_executor import AgentExecutor
from core.knowledge_base import knowledge_base, KnowledgeBaseError
from core.llm_registry import LLMRegistry
from core.prompt_builder import prompt_builder
from core.tools.factory import build_registry_for_task
from evals.evaluators.judge import evaluate_judge
from evals.evaluators.plan import evaluate_plan
from evals.evaluators.tools import evaluate_tools
from evals.schemas import (
    DeterministicResult, EvalCase, EvalResult, EvalRunSummary,
)
from core.handler import _make_submit_report_tool, _to_lc_messages
from core.prompt_version_registry import PromptVersionNotFoundError
from models import DocumentMetadata, TaskMessage

logger = logging.getLogger(__name__)

_DATASET_DIR = Path(__file__).parent / "dataset"
_RESULTS_DIR = Path(__file__).parent / "results"


def _load_cases(procedure: str) -> list[EvalCase]:
    path = _DATASET_DIR / f"{procedure}.json"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**c) for c in raw]


def _resolve_url(document_url: str) -> str:
    """Resolve relative fixture paths to absolute file:// URLs."""
    if document_url.startswith(("file://", "http://", "https://")):
        return document_url
    abs_path = (_DATASET_DIR.parent / document_url).resolve()
    return f"file://{abs_path}"


def _build_task(case: EvalCase) -> TaskMessage:
    doc = None
    if case.document_url:
        url = _resolve_url(case.document_url)
        suffix = Path(case.document_url).suffix.lower().lstrip(".")
        fmt = {"jpg": "JPG", "jpeg": "JPG", "png": "PNG", "pdf": "PDF", "docx": "DOCX"}.get(suffix, suffix.upper())
        abs_path = Path(url.replace("file://", ""))
        file_size = abs_path.stat().st_size if abs_path.exists() else None
        doc = DocumentMetadata(
            file_name=Path(case.document_url).name,
            file_url=url,
            file_format=fmt,
            file_size=file_size,
        )
    return TaskMessage(
        application_id=f"eval-{case.case_id}",
        procedure=case.procedure,
        form_data=case.form_data,
        document=doc,
    )


async def run_case(
    case: EvalCase,
    prompt_version: str,
    judge_model: str,
) -> EvalResult:
    start = time.monotonic()
    task = _build_task(case)

    try:
        procedure_text = knowledge_base.load(case.procedure)
    except KnowledgeBaseError as exc:
        logger.error("Case %s: procedure not found: %s", case.case_id, exc)
        procedure_text = ""

    try:
        raw_messages = prompt_builder.build(task, procedure_text, prompt_version)
    except PromptVersionNotFoundError as exc:
        logger.error("Case %s: prompt build failed: %s", case.case_id, exc)
        raw_messages = []

    messages = _to_lc_messages(raw_messages)

    tool_registry = build_registry_for_task(task)
    submit_tool = _make_submit_report_tool()
    all_tools = tool_registry.as_langchain_tools() + [submit_tool]
    model = LLMRegistry.get(settings.default_model).bind_tools(all_tools)

    executor = AgentExecutor(model, tool_registry, max_iterations=20)
    submit_args, trace = await executor.run(messages)

    elapsed = int(time.monotonic() - start)
    actual_decision = (submit_args or {}).get("decision")

    # Deterministic evaluation
    tool_result = evaluate_tools(case, trace)
    plan_score, plan_violations = evaluate_plan(case, trace)

    det = DeterministicResult(
        decision_correct=(actual_decision == case.expected_decision),
        plan_score=plan_score,
        tool_score=tool_result.tool_score,
        plan_violations=plan_violations,
        tool_violations=tool_result.tool_violations,
    )

    # LLM-as-Judge
    judge = await evaluate_judge(
        case=case,
        procedure_text=procedure_text,
        trace=trace,
        submit_args=submit_args or {},
        model_name=judge_model,
    )

    return EvalResult(
        case_id=case.case_id,
        description=case.description,
        expected_decision=case.expected_decision,
        actual_decision=actual_decision,
        deterministic=det,
        judge=judge,
        processing_time_seconds=elapsed,
    )


async def run_eval(
    procedure: str,
    prompt_version: str | None = None,
    judge_model: str | None = None,
    case_ids: list[str] | None = None,
) -> EvalRunSummary:
    version = prompt_version or settings.prompt_version
    judge = judge_model or settings.eval_judge_model

    cases = _load_cases(procedure)
    if case_ids:
        cases = [c for c in cases if c.case_id in case_ids]
    logger.info("Running %d eval cases for procedure=%s prompt=%s", len(cases), procedure, version)

    results = []
    for case in cases:
        logger.info("  → %s: %s", case.case_id, case.description)
        result = await run_case(case, version, judge)
        results.append(result)
        status = "✓" if result.deterministic.decision_correct else "✗"
        logger.info(
            "    %s decision=%s plan=%.2f tool=%.2f judge=%.2f",
            status,
            result.actual_decision,
            result.deterministic.plan_score,
            result.deterministic.tool_score,
            result.judge.judge_score,
        )

    accuracy = sum(1 for r in results if r.deterministic.decision_correct) / len(results)
    summary = EvalRunSummary(
        procedure=procedure,
        prompt_version=version,
        model=settings.default_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_cases=len(results),
        accuracy=round(accuracy, 3),
        mean_plan_score=round(sum(r.deterministic.plan_score for r in results) / len(results), 3),
        mean_tool_score=round(sum(r.deterministic.tool_score for r in results) / len(results), 3),
        mean_judge_score=round(sum(r.judge.judge_score for r in results) / len(results), 3),
        results=results,
    )

    _RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = _RESULTS_DIR / f"{ts}_{procedure}.json"
    out_path.write_text(
        json.dumps(asdict(summary), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Results written to %s", out_path)

    # Print summary table
    print(f"\n{'='*60}")
    print(f"Procedure:    {procedure}")
    print(f"Prompt:       {version}  |  Model: {settings.default_model}")
    print(f"Cases:        {len(results)}")
    print(f"Accuracy:     {accuracy:.0%}")
    print(f"Plan score:   {summary.mean_plan_score:.2f}")
    print(f"Tool score:   {summary.mean_tool_score:.2f}")
    print(f"Judge score:  {summary.mean_judge_score:.2f}")
    print(f"{'='*60}\n")

    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    parser = argparse.ArgumentParser(description="Run agent eval suite")
    parser.add_argument("--procedure", required=True)
    parser.add_argument("--prompt-version", default=None)
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--cases", nargs="+", default=None, metavar="CASE_ID")
    args = parser.parse_args()

    asyncio.run(run_eval(args.procedure, args.prompt_version, args.judge_model, args.cases))
