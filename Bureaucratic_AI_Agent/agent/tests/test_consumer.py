import json
import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from consumer import on_message
from models import AIReportPayload


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_message(body: bytes) -> MagicMock:
    """Minimal AbstractIncomingMessage stub."""
    message = MagicMock()
    message.body = body

    @asynccontextmanager
    async def _process(**kwargs):
        yield

    message.process = _process
    return message


def _valid_body() -> bytes:
    return json.dumps({
        "application_id": "00000000-0000-0000-0000-000000000001",
        "procedure": "passport_md",
        "form_data": {"first_name": "Ivan"},
        "document": None,
    }).encode()


def _stub_report() -> AIReportPayload:
    return AIReportPayload(
        application_id="00000000-0000-0000-0000-000000000001",
        decision="ACCEPT",
        validation_result={},
        extracted_data={},
        issues_found=[],
        recommendations="",
        processing_time_seconds=1,
        ai_model_used="stub",
    )


# ── tests ─────────────────────────────────────────────────────────────────────

async def test_on_message_happy_path():
    """Valid payload → handle_task called → send_callback called."""
    report = _stub_report()

    with (
        patch("consumer.handle_task", AsyncMock(return_value=report)) as mock_handle,
        patch("consumer.send_callback", AsyncMock()) as mock_callback,
    ):
        await on_message(_make_message(_valid_body()))

    mock_handle.assert_awaited_once()
    task_arg = mock_handle.call_args[0][0]
    assert task_arg.procedure == "passport_md"
    assert task_arg.application_id == "00000000-0000-0000-0000-000000000001"

    mock_callback.assert_awaited_once_with(report)


async def test_on_message_invalid_json_is_swallowed():
    """Non-JSON body → error logged, no exception raised, handle_task never called."""
    with (
        patch("consumer.handle_task", AsyncMock()) as mock_handle,
        patch("consumer.send_callback", AsyncMock()),
    ):
        await on_message(_make_message(b"not-json"))  # must not raise

    mock_handle.assert_not_awaited()


async def test_on_message_invalid_schema_is_swallowed():
    """Valid JSON but wrong shape → error logged, handle_task never called."""
    body = json.dumps({"unexpected": "field"}).encode()

    with (
        patch("consumer.handle_task", AsyncMock()) as mock_handle,
        patch("consumer.send_callback", AsyncMock()),
    ):
        await on_message(_make_message(body))

    mock_handle.assert_not_awaited()


async def test_on_message_handle_task_raises_propagates():
    """Exception from handle_task propagates out (triggers aio_pika requeue)."""
    with (
        patch("consumer.handle_task", AsyncMock(side_effect=RuntimeError("boom"))),
        patch("consumer.send_callback", AsyncMock()) as mock_callback,
    ):
        with pytest.raises(RuntimeError, match="boom"):
            await on_message(_make_message(_valid_body()))

    mock_callback.assert_not_awaited()
