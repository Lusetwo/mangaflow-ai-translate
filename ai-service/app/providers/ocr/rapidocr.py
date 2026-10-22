import asyncio
import io
from PIL import Image
from app.core.exceptions import ProviderError
from app.providers.ocr.base import OCRProvider


"""一个基于 RapidOCR 的 OCR 识别器：接收图片字节，识别出图中的文字及其位置，返回结构化的"文字区域列表"""
class RapidOCRProvider(OCRProvider):
    def __init__(self):
        self._engine = None

    def _recognize_sync(self, image_bytes: bytes) -> list[dict]:
        try:
            import numpy as np
            from rapidocr_onnxruntime import RapidOCR
            if self._engine is None:
                self._engine = RapidOCR()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            result, _ = self._engine(np.array(image))
            regions = []
            for index, item in enumerate(result or []):
                box, text, score = item
                xs, ys = [p[0] for p in box], [p[1] for p in box]
                regions.append({"id": f"region-{index + 1}", "text": str(text), "confidence": float(score),
                    "x": int(min(xs)), "y": int(min(ys)),
                    "width": max(1, int(max(xs) - min(xs))), "height": max(1, int(max(ys) - min(ys)))})
            return regions
        except Exception as exc:
            raise ProviderError("OCR recognition failed") from exc

    async def recognize(self, image_bytes: bytes) -> list[dict]:
        return await asyncio.to_thread(self._recognize_sync, image_bytes)
