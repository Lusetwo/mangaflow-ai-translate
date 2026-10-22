import asyncio
import io
from PIL import Image, ImageDraw
from app.providers.image.base import ImageRenderer
from app.providers.image.pillow_typesetter import PillowTypesetter


"""预览框渲染 + 最终嵌字：预览画 OCR 框；compose 委托 Typesetter。"""
class PillowPreviewRenderer(ImageRenderer):
    def __init__(self):
        self._typesetter = PillowTypesetter()

    def _render(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)
        label = "MangaFlow AI - Agent Preview"
        draw.rounded_rectangle((8, 8, min(image.width - 1, 280), 38), radius=6, fill="white", outline="#777")
        draw.text((15, 15), label, fill="#222")
        for region in regions:
            x, y = region["x"], region["y"]
            draw.rectangle((x, y, x + region["width"], y + region["height"]), outline="#00a0ff", width=2)
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    async def render_preview(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        return await asyncio.to_thread(self._render, image_bytes, regions, translations)

    async def compose(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        return await self._typesetter.compose(image_bytes, regions, translations)
