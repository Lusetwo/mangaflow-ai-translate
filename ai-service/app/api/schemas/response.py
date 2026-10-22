from typing import Any
from pydantic import BaseModel

class AgentTraceItem(BaseModel):
    step: str
    tool: str | None = None
    status: str
    duration_ms: int = 0
    detail: str | None = None

class AgentExecutionResponse(BaseModel):
    status: str
    sourceLang: str
    targetLang: str
    ocrMode: str
    translationMode: str
    regions: list[dict[str, Any]]
    translations: list[str]
    resultImageBase64: str
    resultMimeType: str = "image/png"
    notice: str
    executionTrace: list[AgentTraceItem] = []
