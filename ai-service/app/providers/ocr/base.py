from abc import ABC, abstractmethod

class OCRProvider(ABC):
    @abstractmethod
    async def recognize(self, image_bytes: bytes) -> list[dict]:
        raise NotImplementedError
