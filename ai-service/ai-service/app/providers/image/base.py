from abc import ABC, abstractmethod


class ImageRenderer(ABC):
    @abstractmethod
    async def render_preview(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def compose(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        raise NotImplementedError
