from app.providers.inpaint.base import InpaintingProvider


class DemoInpaintingProvider(InpaintingProvider):
    async def inpaint(self, image_bytes: bytes, regions: list[dict]) -> bytes:
        return image_bytes
