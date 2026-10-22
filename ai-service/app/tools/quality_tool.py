from typing import Any
from app.agent.context import AgentContext
from app.core.config import settings
from app.tools.base import AgentTool

class QualityCheckTool(AgentTool):
    name = "quality_check"
    description = "Check basic OCR/translation consistency and flag low-confidence text for review."
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        low = [r.get("id", str(i)) for i, r in enumerate(context.regions) if float(r.get("confidence", 1.0)) < settings.min_ocr_confidence]
        missing = [i for i, value in enumerate(context.translations) if not value.strip()]
        report = {"passed": not low and not missing, "low_confidence_region_ids": low, "missing_translation_indexes": missing,
                  "requires_review": bool(low or missing), "checks": ["ocr_confidence", "translation_presence"]}
        context.quality_report = report
        return report
