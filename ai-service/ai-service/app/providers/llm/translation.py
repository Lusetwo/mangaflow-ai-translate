from app.providers.llm.base import LLMProvider, TranslationProvider


"""基于统一 LLMProvider 的翻译适配：业务侧只拼 prompt，不绑定具体模型厂商。"""
class LLMTranslationProvider(TranslationProvider):
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        prompt = (
            "You are a professional manga localization translator. Translate the dialogue naturally, "
            "preserve tone and character voice, and return only the translated text. "
            f"Source language: {source_lang}. Target language: {target_lang}.\n\n{text}"
        )
        return await self.llm.complete(prompt)
