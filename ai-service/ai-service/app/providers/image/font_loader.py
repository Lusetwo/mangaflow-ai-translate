from functools import lru_cache
from pathlib import Path
from PIL import ImageFont
from app.core.config import settings

_WINDOWS_FONTS = (
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\arialuni.ttf",
)


@lru_cache(maxsize=16)
def load_font(size: int) -> ImageFont.ImageFont:
    candidates: list[str] = []
    if settings.font_path:
        candidates.append(settings.font_path)
    candidates.extend(_WINDOWS_FONTS)
    for path in candidates:
        if path and Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()
