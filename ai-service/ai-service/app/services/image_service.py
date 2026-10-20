import io
from PIL import Image, UnidentifiedImageError
from app.core.exceptions import MangaFlowError

class InvalidImageError(MangaFlowError): pass

def validate_image(data: bytes) -> tuple[int, int, str]:
    try:
        image = Image.open(io.BytesIO(data))
        image.verify()
        image = Image.open(io.BytesIO(data))
        return image.width, image.height, image.format or "unknown"
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise InvalidImageError("Invalid or corrupted image") from exc
