from models import TaskMessage
from core.tools import ToolRegistry
from core.tools.document import build_document_registry
from core.tools.utils import build_utils_registry


def build_registry_for_task(task: TaskMessage) -> ToolRegistry:
    """Assembles the full tool registry for a task: document tools + utility tools."""
    registry = build_document_registry(task)
    for tool in build_utils_registry()._tools.values():
        registry.register(tool)
    return registry
