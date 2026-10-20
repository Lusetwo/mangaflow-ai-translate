from abc import ABC, abstractmethod
from typing import Any
from app.agent.context import AgentContext


class AgentTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
