from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.providers.inpaint.base import InpaintingProvider
from app.providers.inpaint.demo import DemoInpaintingProvider
from app.providers.inpaint.lama_onnx import LamaOnnxInpaintingProvider
from app.providers.inpaint.opencv import OpenCVInpaintingProvider


def create_inpaint_provider() -> InpaintingProvider:
    name = settings.inpaint_provider
    if name == "demo":
        return DemoInpaintingProvider()
    if name == "opencv":
        return OpenCVInpaintingProvider()
    if name == "lama":
        return LamaOnnxInpaintingProvider()
    raise ConfigurationError(f"Unsupported INPAINT_PROVIDER={name}")
