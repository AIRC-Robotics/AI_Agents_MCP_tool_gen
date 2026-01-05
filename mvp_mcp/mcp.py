from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict

ToolFunc = Callable[..., Awaitable[Any]]


@dataclass
class ToolDefinition:
    name: str
    description: str
    func: ToolFunc


class FastMCP:
    def __init__(self, name: str) -> None:
        self.name = name
        self._tools: Dict[str, ToolDefinition] = {}

    def tool(self) -> Callable[[ToolFunc], ToolFunc]:
        def decorator(func: ToolFunc) -> ToolFunc:
            description = func.__doc__ or ""
            self._tools[func.__name__] = ToolDefinition(
                name=func.__name__,
                description=description.strip(),
                func=func,
            )
            return func

        return decorator

    def list_tools(self) -> Dict[str, ToolDefinition]:
        return dict(self._tools)

    async def call_tool(self, name: str, params: Dict[str, Any]) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return await self._tools[name].func(**params)
