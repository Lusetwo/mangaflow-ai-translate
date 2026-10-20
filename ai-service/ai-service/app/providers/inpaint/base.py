from abc import ABC, abstractmethod


class InpaintingProvider(ABC):
    @abstractmethod
    async def inpaint(self, image_bytes: bytes, regions: list[dict]) -> bytes:
        raise NotImplementedError
