from app.agent.context import AgentContext
from app.core.enums import WorkflowStep


class MangaPlanner:
    """Deterministic workflow planner; LLM-based tool selection can be added behind this interface later."""
    def plan(self, context: AgentContext) -> list[tuple[WorkflowStep, str]]:
        steps = [
            (WorkflowStep.VALIDATE, ""),
            (WorkflowStep.OCR, "ocr"),
            (WorkflowStep.TRANSLATE, "translate"),
            (WorkflowStep.INPAINT, "inpaint"),
            (WorkflowStep.TYPESET, "typeset"),
        ]
        if context.options.get("quality_check", True):
            steps.append((WorkflowStep.QUALITY_CHECK, "quality_check"))
        steps.append((WorkflowStep.COMPLETED, ""))
        return steps
