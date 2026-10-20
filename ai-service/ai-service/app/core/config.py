from dataclasses import dataclass
import os
from dotenv import load_dotenv
from pathlib import Path

# 项目根目录下的 ai-service/.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
# .env 覆盖进程环境，避免旧 shell 里残留的 LLM_PROVIDER=gemini 盖住新配置
load_dotenv(ENV_FILE, override=True)

@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("SERVICE_NAME", "mangaflow-ai")
    environment: str = os.getenv("APP_ENV", "local")
    max_image_bytes: int = int(os.getenv("MAX_IMAGE_BYTES", str(20 * 1024 * 1024)))
    ocr_provider: str = os.getenv("OCR_PROVIDER", os.getenv("OCR_MODE", "demo")).lower()
    llm_provider: str = os.getenv("LLM_PROVIDER", os.getenv("TRANSLATION_MODE", "demo")).lower()
    # 统一大模型配置；兼容旧 GEMINI_* / DEEPSEEK_API_KEY
    llm_api_key: str = (
        os.getenv("LLM_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or ""
    ).strip()
    llm_model: str = (os.getenv("LLM_MODEL") or os.getenv("GEMINI_MODEL") or "").strip()
    llm_base_url: str = (os.getenv("LLM_BASE_URL") or os.getenv("GEMINI_BASE_URL") or "").rstrip("/")
    llm_timeout_seconds: float = float(
        os.getenv("LLM_TIMEOUT_SECONDS") or os.getenv("GEMINI_TIMEOUT_SECONDS") or "45"
    )
    llm_http_proxy: str = (
        os.getenv("LLM_HTTP_PROXY", "").strip()
        or os.getenv("GEMINI_HTTP_PROXY", "").strip()
        or os.getenv("HTTPS_PROXY", "").strip()
        or os.getenv("HTTP_PROXY", "").strip()
    )
    inpaint_provider: str = os.getenv("INPAINT_PROVIDER", "lama").lower()
    inpaint_mask_padding: int = int(os.getenv("INPAINT_MASK_PADDING", "6"))
    font_path: str = os.getenv("FONT_PATH", "").strip()
    max_agent_steps: int = int(os.getenv("MAX_AGENT_STEPS", "8"))
    min_ocr_confidence: float = float(os.getenv("MIN_OCR_CONFIDENCE", "0.45"))
    translation_concurrency: int = max(1, int(os.getenv("TRANSLATION_CONCURRENCY", "4")))
    cors_origins: tuple[str, ...] = tuple(x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip())

settings = Settings()
