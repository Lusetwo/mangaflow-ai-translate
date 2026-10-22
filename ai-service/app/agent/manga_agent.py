from app.agent.context import AgentContext
from app.agent.planner import MangaPlanner
from app.agent.tool_executor import ToolExecutor
from app.agent.tool_registry import ToolRegistry
from app.core.enums import AgentStatus, WorkflowStep
from app.core.exceptions import MangaFlowError
from app.tools.inpainting_tool import InpaintTool
from app.tools.ocr_tool import OCRTool
from app.tools.quality_tool import QualityCheckTool
from app.tools.translation_tool import TranslationTool
from app.tools.typesetting_tool import PreviewRenderTool, TypesetTool


class MangaAgent:
    def __init__(self):
        registry = ToolRegistry()
        for tool in (OCRTool(), TranslationTool(), InpaintTool(), TypesetTool(), PreviewRenderTool(), QualityCheckTool()):
            registry.register(tool)
        self.registry = registry
        self.executor = ToolExecutor(registry)
        self.planner = MangaPlanner()

    async def run(self, context: AgentContext) -> AgentContext:
        context.state.status = AgentStatus.RUNNING
        try:
            for step, tool_name in self.planner.plan(context):
                context.state.enter(step)
                if step == WorkflowStep.VALIDATE:
                    if not context.image_bytes:
                        raise ValueError("Image bytes cannot be empty")
                    context.state.complete(step)
                    continue
                if step == WorkflowStep.COMPLETED:
                    context.state.complete(step)
                    break
                await self.executor.execute(tool_name, context)
                context.state.complete(step)
            context.state.status = AgentStatus.NEEDS_REVIEW \
                if context.quality_report.get("requires_review") else AgentStatus.SUCCEEDED
            return context
        except Exception as exc:
            context.state.status = AgentStatus.FAILED
            context.state.errors.append(type(exc).__name__)
            if isinstance(exc, MangaFlowError):
                raise
            raise
