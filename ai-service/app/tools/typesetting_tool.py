from typing import Any
from app.agent.context import AgentContext
from app.providers.image.pillow_renderer import PillowPreviewRenderer
from app.tools.base import AgentTool


class PreviewRenderTool(AgentTool):
    name = "render_preview"
    description = "Create an annotated OCR preview image; this does not remove original text."
    def __init__(self):
        self.renderer = PillowPreviewRenderer()
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        context.result_image_bytes = await self.renderer.render_preview(
            context.image_bytes, context.regions, context.translations
        )
        return {"mime_type": "image/png", "bytes": len(context.result_image_bytes), "mode": "annotated_preview"}


class TypesetTool(AgentTool):
    name = "typeset"
    description = "Embed translated text into the cleaned manga image within OCR bounding boxes."
    def __init__(self):
        self.renderer = PillowPreviewRenderer()
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        base = context.cleaned_image_bytes or context.image_bytes
        context.result_image_bytes = await self.renderer.compose(base, context.regions, context.translations)
        return {
            "mime_type": "image/png",
            "bytes": len(context.result_image_bytes),
            "mode": "composed",
            "used_cleaned": context.cleaned_image_bytes is not None,
        }
