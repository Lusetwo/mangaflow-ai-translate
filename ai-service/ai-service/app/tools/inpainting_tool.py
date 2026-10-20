from typing import Any
from app.agent.context import AgentContext
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.inpaint.factory import create_inpaint_provider
from app.providers.inpaint.opencv import OpenCVInpaintingProvider
from app.tools.base import AgentTool


class InpaintTool(AgentTool):
    name = "inpaint"
    description = "Remove original text from OCR regions using inpainting before typesetting."
    def __init__(self):
        self.provider = create_inpaint_provider()
        # lama 依赖外部模型下载，失败时回退 opencv，保证原文仍能被擦除
        self.fallback = OpenCVInpaintingProvider() if settings.inpaint_provider == "lama" else None
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        provider = settings.inpaint_provider
        try:
            context.cleaned_image_bytes = await self.provider.inpaint(context.image_bytes, context.regions)
        except ProviderError:
            if self.fallback is None:
                raise
            context.cleaned_image_bytes = await self.fallback.inpaint(context.image_bytes, context.regions)
            provider = "opencv"
        return {
            "bytes": len(context.cleaned_image_bytes),
            "region_count": len(context.regions),
            "provider": provider,
        }
