"""Thin workflow node wrappers; keeping these separate makes each stage testable."""
from app.agent.context import AgentContext
from app.agent.tool_executor import ToolExecutor


class WorkflowNodes:
    def __init__(self, executor: ToolExecutor):
        self.executor = executor
    async def run_ocr(self, context: AgentContext) -> dict:
        return await self.executor.execute("ocr", context)
    async def run_translation(self, context: AgentContext) -> dict:
        return await self.executor.execute("translate", context)
    async def run_inpaint(self, context: AgentContext) -> dict:
        return await self.executor.execute("inpaint", context)
    async def run_typeset(self, context: AgentContext) -> dict:
        return await self.executor.execute("typeset", context)
    async def render_preview(self, context: AgentContext) -> dict:
        return await self.executor.execute("render_preview", context)
    async def quality_check(self, context: AgentContext) -> dict:
        return await self.executor.execute("quality_check", context)
