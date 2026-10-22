import asyncio
import io
import cv2
import numpy as np
from PIL import Image
from app.core.exceptions import ProviderError
from app.providers.inpaint.base import InpaintingProvider
from app.providers.inpaint.mask import build_region_mask


"""OpenCV TELEA 轻量擦除：无 LaMa 模型时的可用回退。"""
class OpenCVInpaintingProvider(InpaintingProvider):
    def _inpaint_sync(self, image_bytes: bytes, regions: list[dict]) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            arr = np.array(image)
            mask = build_region_mask(arr.shape[0], arr.shape[1], regions)
            if not mask.any():
                return image_bytes
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            repaired = cv2.inpaint(bgr, mask, 3, cv2.INPAINT_TELEA)
            rgb = cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB)
            output = io.BytesIO()
            Image.fromarray(rgb).save(output, format="PNG")
            return output.getvalue()
        except Exception as exc:
            raise ProviderError("OpenCV inpainting failed") from exc

    async def inpaint(self, image_bytes: bytes, regions: list[dict]) -> bytes:
        return await asyncio.to_thread(self._inpaint_sync, image_bytes, regions)
