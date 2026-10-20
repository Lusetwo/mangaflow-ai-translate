import time
from app.agent.context import AgentContext
from app.agent.tool_registry import ToolRegistry
from app.core.exceptions import ToolExecutionError

class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    async def execute(self, name: str, context: AgentContext, arguments: dict | None = None) -> dict:
        tool = self.registry.get(name)
        started = time.perf_counter()
        try:
            result = await tool.execute(context, arguments or {})
            context.state.trace.append({"step": context.state.current_step.value, "tool": name, "status": "SUCCEEDED",
                "duration_ms": int((time.perf_counter() - started) * 1000), "detail": f"tool={name}"})
            return result
        except Exception as exc:
            context.state.trace.append({"step": context.state.current_step.value, "tool": name, "status": "FAILED",
                "duration_ms": int((time.perf_counter() - started) * 1000), "detail": type(exc).__name__})
            cause = str(exc).strip()
            detail = f"Tool '{name}' failed: {cause}" if cause else f"Tool '{name}' failed"
            raise ToolExecutionError(detail) from exc
