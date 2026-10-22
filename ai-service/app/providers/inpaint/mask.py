import numpy as np
from app.core.config import settings


def build_region_mask(height: int, width: int, regions: list[dict], padding: int | None = None) -> np.ndarray:
    """Generate a binary mask (uint8, 0/255) covering OCR regions with padding."""
    pad = settings.inpaint_mask_padding if padding is None else padding
    mask = np.zeros((height, width), dtype=np.uint8)
    for region in regions:
        x = max(0, int(region.get("x", 0)) - pad)
        y = max(0, int(region.get("y", 0)) - pad)
        w = max(1, int(region.get("width", 1)) + pad * 2)
        h = max(1, int(region.get("height", 1)) + pad * 2)
        x2 = min(width, x + w)
        y2 = min(height, y + h)
        mask[y:y2, x:x2] = 255
    return mask
