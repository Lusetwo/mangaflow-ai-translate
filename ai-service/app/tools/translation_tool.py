import asyncio
import logging
from typing import Any
from app.agent.context import AgentContext
from app.core.config import settings
from app.providers.llm.factory import create_translation_provider
from app.tools.base import AgentTool

log = logging.getLogger(__name__)


class TranslationTool(AgentTool):
    name = "translate"
    description = "Translate detected manga dialogue while preserving tone and character voice."

    def __init__(self):
        self.provider = create_translation_provider()

    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        texts = [region.get("text", "").strip() for region in context.regions]

        if not texts:
            context.translations = []
            return {"translation_count": 0, "translations": [], "provider": settings.llm_provider}

        # 批量：一次 LLM 调用替代 N 次并发 HTTP 往返
        output = await self.provider.translate_batch(texts, context.source_lang, context.target_lang)

        # 长度兜底，确保和输入段数一一对应
        if len(output) != len(texts):
            log.warning("batch output len mismatch: got %d want %d, padding", len(output), len(texts))
            if len(output) < len(texts):
                output = output + [""] * (len(texts) - len(output))
            else:
                output = output[: len(texts)]

        context.translations = output
        return {"translation_count": len(output), "translations": output, "provider": settings.llm_provider}
