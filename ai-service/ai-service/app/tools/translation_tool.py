import asyncio
from typing import Any
from app.agent.context import AgentContext
from app.core.config import settings
from app.providers.llm.factory import create_translation_provider
from app.tools.base import AgentTool

class TranslationTool(AgentTool):
    name = "translate"
    description = "Translate detected manga dialogue while preserving tone and character voice."
    def __init__(self):
        self.provider = create_translation_provider()
    async def execute(self, context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        texts = [region.get("text", "").strip() for region in context.regions]
        semaphore = asyncio.Semaphore(settings.translation_concurrency)

        async def translate_one(text: str) -> str:
            if not text:
                return ""
            async with semaphore:
                return await self.provider.translate(text, context.source_lang, context.target_lang)

        output = list(await asyncio.gather(*(translate_one(t) for t in texts)))
        context.translations = output
        return {"translation_count": len(output), "translations": output, "provider": settings.llm_provider}
