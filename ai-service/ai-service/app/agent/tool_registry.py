from app.core.exceptions import ToolNotFoundError
from app.tools.base import AgentTool

class ToolRegistry:
    def __init__(self): self._tools: (
        dict)[str, AgentTool] = {}
    def register(self, tool: AgentTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool: {tool.name}")
        self._tools[tool.name] = tool
    def get(self, name: str) -> AgentTool:
        if name not in self._tools:
            raise ToolNotFoundError(f"Unknown tool: {name}")
        return self._tools[name]
    def descriptions(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]
    def names(self) -> list[str]: return list(self._tools.keys())
