from datetime import datetime, timezone
from typing import Any

from core.tools import Tool, ToolRegistry


async def _get_current_datetime() -> str:
    """Returns the current UTC date and time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


async def _call_external_api(endpoint: str, params: dict[str, Any] | None = None) -> str:
    return f"[stub] {endpoint} → 200 OK {{'valid': true, 'params': {params or {}}}}"


_UTILS_TOOLS = [
    Tool(
        name="get_current_datetime",
        description="Returns the current UTC date and time. Use this to check document expiry dates.",
        parameters={"type": "object", "properties": {}, "required": []},
        fn=lambda: _get_current_datetime(),
    ),
    Tool(
        name="call_external_api",
        description="Call a mock external government API to cross-validate applicant data.",
        parameters={
            "type": "object",
            "properties": {
                "endpoint": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["endpoint"],
        },
        fn=_call_external_api,
    ),
]


def build_utils_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in _UTILS_TOOLS:
        registry.register(tool)
    return registry
