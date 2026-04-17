import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trace interface
# ---------------------------------------------------------------------------

class _NoOpTrace:
    """Used when LangFuse is not configured or unavailable."""
    def record_generation(self, **_: Any) -> None: pass
    def record_tool(self, **_: Any) -> None: pass
    def end(self, **_: Any) -> None: pass
    def now(self) -> datetime: return datetime.now(timezone.utc)


class _LangFuseTrace:
    def __init__(self, client: Any, trace: Any) -> None:
        self._client = client
        self._trace = trace

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def record_generation(
        self,
        name: str,
        model: str,
        input_messages: list,
        output: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> None:
        self._trace.generation(
            name=name,
            model=model,
            input=input_messages,
            output=output,
            usage={
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
                "unit": "TOKENS",
            },
            metadata={"latency_ms": latency_ms},
            start_time=start_time,
            end_time=end_time,
        )

    def record_tool(
        self, name: str, args: dict, result: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> None:
        self._trace.event(
            name=f"tool:{name}",
            input=args,
            output=result[:500],
            start_time=start_time,
        )

    def end(self, decision: str | None, iterations: int, elapsed_ms: int) -> None:
        self._trace.update(
            output={"decision": decision, "iterations": iterations},
            tags=[f"decision:{decision or 'none'}"],
            metadata={"elapsed_ms": elapsed_ms},
        )
        self._client.flush()


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

@asynccontextmanager
async def agent_trace(task: Any):
    """
    Async context manager yielding a trace object for one agent run.
    Yields _NoOpTrace if LangFuse is not configured or fails to connect.

    Usage:
        async with agent_trace(task) as trace:
            trace.record_generation(...)
    """
    if not (settings.langfuse_host and settings.langfuse_public_key and settings.langfuse_secret_key):
        yield _NoOpTrace()
        return

    try:
        from langfuse import Langfuse
        client = Langfuse(
            host=settings.langfuse_host,
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
        )
        trace = client.trace(
            name="agent_run",
            id=task.application_id,
            input={"procedure": task.procedure, "has_document": task.document is not None},
            metadata={
                "procedure": task.procedure,
                "application_id": task.application_id,
            },
        )
        yield _LangFuseTrace(client, trace)
    except Exception as exc:
        logger.warning("LangFuse unavailable — observability disabled: %s", exc)
        yield _NoOpTrace()
