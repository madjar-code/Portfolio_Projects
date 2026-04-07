from dataclasses import dataclass
from typing import Any, Callable, Awaitable
from langchain_core.tools import StructuredTool
from core.tools._utils import _schema_to_pydantic


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Awaitable[str]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    async def execute(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'"
        return await tool.fn(**arguments)

    def as_langchain_tools(self) -> list[StructuredTool]:
        """Convert registered tools to LangChain StructuredTools for model.bind_tools()."""
        result = []
        for tool in self._tools.values():
            result.append(
                StructuredTool.from_function(
                    coroutine=tool.fn,
                    name=tool.name,
                    description=tool.description,
                    args_schema=_schema_to_pydantic(tool.name, tool.parameters),
                )
            )
        return result
