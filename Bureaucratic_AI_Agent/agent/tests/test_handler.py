import pytest
from models import TaskMessage
from core.handler import handle_task


def _make_task(procedure: str) -> TaskMessage:
    return TaskMessage(
        application_id="00000000-0000-0000-0000-000000000001",
        procedure=procedure,
        form_data={"first_name": "Ivan"},
        document=None,
    )


async def test_handle_task_known_procedure_returns_accept():
    result = await handle_task(_make_task("passport_md"))

    assert result.decision == "ACCEPT"
    assert result.application_id == "00000000-0000-0000-0000-000000000001"
    assert result.processing_time_seconds > 0


async def test_handle_task_unknown_procedure_returns_reject():
    result = await handle_task(_make_task("nonexistent_procedure"))

    assert result.decision == "REJECT"
    assert result.processing_time_seconds == 0
    assert any(i["type"] == "configuration_error" for i in result.issues_found)
