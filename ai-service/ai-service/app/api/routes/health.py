from fastapi import APIRouter
from app.core.config import settings
router = APIRouter()
@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "UP",
        "service": settings.service_name,
        "ocr_provider": settings.ocr_provider,
        "llm_provider": settings.llm_provider,
        "inpaint_provider": settings.inpaint_provider,
    }
