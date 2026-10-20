from typing import Any
from app.agent.context import AgentContext
from app.core.config import settings
from app.providers.ocr.demo import DemoOCRProvider
from app.providers.ocr.rapidocr import RapidOCRProvider
from app.tools.base import AgentTool

class OCRTool(AgentTool):
    name = "ocr"
    description = "Detect text regions and return text, bounding boxes, and confidence scores."
    def __init__(self):
        self.provider = RapidOCRProvider() if settings.ocr_provider == "rapidocr" else DemoOCRProvider()
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        context.regions = await self.provider.recognize(context.image_bytes)
        return {"region_count": len(context.regions), "regions": context.regions, "provider": settings.ocr_provider}
