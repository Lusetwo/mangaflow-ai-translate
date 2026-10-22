from app.providers.llm.base import LLMProvider, TranslationProvider


class DemoLLMProvider(LLMProvider):
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        return f"[演示回复] {prompt[:80]}"


class DemoTranslationProvider(TranslationProvider):
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"[演示译文] {text}"
