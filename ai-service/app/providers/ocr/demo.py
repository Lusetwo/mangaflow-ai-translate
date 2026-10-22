from app.providers.ocr.base import OCRProvider

class DemoOCRProvider(OCRProvider):
    async def recognize(self, image_bytes: bytes) -> list[dict]:
        # Explicitly empty: never invent OCR text when running in demo mode.
        return []
