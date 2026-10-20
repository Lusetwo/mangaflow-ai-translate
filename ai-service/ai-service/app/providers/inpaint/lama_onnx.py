import asyncio
import io
import shutil
from pathlib import Path
import urllib.request
import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.inpaint.base import InpaintingProvider
from app.providers.inpaint.mask import build_region_mask

# 优先官方源，失败后回退国内镜像，避免 huggingface.co 网络不通导致无法擦除
_MODEL_URLS = (
    "https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx",
    "https://hf-mirror.com/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx",
)
_MODEL_DIR = Path(__file__).resolve().parents[3] / ".cache" / "models"
_MODEL_PATH = _MODEL_DIR / "lama_fp32.onnx"
_INPUT_SIZE = 512
_DOWNLOAD_TIMEOUT_SECONDS = 300


"""LaMa ONNX 擦除：OCR 区域 mask → 512 推理 → 还原分辨率。"""
class LamaOnnxInpaintingProvider(InpaintingProvider):
    def __init__(self):
        self._session: ort.InferenceSession | None = None

    def _download(self, url: str, tmp: Path) -> None:
        handlers = []
        if settings.llm_http_proxy:
            handlers.append(urllib.request.ProxyHandler({
                "http": settings.llm_http_proxy,
                "https": settings.llm_http_proxy,
            }))
        opener = urllib.request.build_opener(*handlers)
        request = urllib.request.Request(url, headers={"User-Agent": "MangaFlow/1.0"})
        with opener.open(request, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as response:
            with open(tmp, "wb") as f:
                shutil.copyfileobj(response, f)

    def _ensure_model(self) -> Path:
        if _MODEL_PATH.exists() and _MODEL_PATH.stat().st_size > 0:
            return _MODEL_PATH
        _MODEL_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _MODEL_PATH.with_suffix(".download")
        last_error: Exception | None = None
        for url in _MODEL_URLS:
            try:
                self._download(url, tmp)
                tmp.replace(_MODEL_PATH)
                return _MODEL_PATH
            except Exception as exc:
                last_error = exc
                if tmp.exists():
                    tmp.unlink(missing_ok=True)
        raise ProviderError(
            "Failed to download LaMa ONNX model; set INPAINT_PROVIDER=opencv as fallback"
        ) from last_error

    def _get_session(self) -> ort.InferenceSession:
        if self._session is None:
            model_path = str(self._ensure_model())
            providers = ["CPUExecutionProvider"]
            available = ort.get_available_providers()
            if "CUDAExecutionProvider" in available:
                providers.insert(0, "CUDAExecutionProvider")
            self._session = ort.InferenceSession(model_path, providers=providers)
        return self._session

    def _inpaint_sync(self, image_bytes: bytes, regions: list[dict]) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            arr = np.array(image)
            h, w = arr.shape[:2]
            mask = build_region_mask(h, w, regions)
            if not mask.any():
                return image_bytes

            image_resized = cv2.resize(arr, (_INPUT_SIZE, _INPUT_SIZE), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(mask, (_INPUT_SIZE, _INPUT_SIZE), interpolation=cv2.INTER_NEAREST)

            image_nchw = image_resized.astype(np.float32).transpose(2, 0, 1)[None] / 255.0
            mask_nchw = (mask_resized.astype(np.float32)[None, None] > 0).astype(np.float32)

            session = self._get_session()
            input_names = [i.name for i in session.get_inputs()]
            feeds = {}
            for name in input_names:
                lowered = name.lower()
                if "mask" in lowered:
                    feeds[name] = mask_nchw
                else:
                    feeds[name] = image_nchw
            outputs = session.run(None, feeds)
            out = outputs[0][0]
            if out.ndim == 3 and out.shape[0] in (1, 3):
                out = out.transpose(1, 2, 0)
            out = np.clip(out * 255.0 if out.max() <= 1.5 else out, 0, 255).astype(np.uint8)
            if out.ndim == 2:
                out = np.stack([out] * 3, axis=-1)
            elif out.shape[2] == 1:
                out = np.repeat(out, 3, axis=2)

            repaired_small = out[:, :, :3]
            repaired = cv2.resize(repaired_small, (w, h), interpolation=cv2.INTER_CUBIC)
            # 仅在 mask 区域贴回，保留非文字区域原细节
            mask_bool = mask > 0
            result = arr.copy()
            result[mask_bool] = repaired[mask_bool]

            output = io.BytesIO()
            Image.fromarray(result).save(output, format="PNG")
            return output.getvalue()
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("LaMa ONNX inpainting failed") from exc

    async def inpaint(self, image_bytes: bytes, regions: list[dict]) -> bytes:
        return await asyncio.to_thread(self._inpaint_sync, image_bytes, regions)
