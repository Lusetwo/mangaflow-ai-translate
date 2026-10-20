from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.providers.llm.base import LLMProvider, TranslationProvider
from app.providers.llm.demo import DemoLLMProvider, DemoTranslationProvider
from app.providers.llm.gemini import GeminiLLMProvider
from app.providers.llm.openai_compat import OpenAICompatLLMProvider
from app.providers.llm.translation import LLMTranslationProvider

_OPENAI_COMPAT_PROVIDERS = {"deepseek", "openai", "openai_compat"}


def create_llm_provider() -> LLMProvider:
    name = settings.llm_provider
    if name == "demo":
        return DemoLLMProvider()
    if name == "gemini":
        return GeminiLLMProvider()
    if name in _OPENAI_COMPAT_PROVIDERS:
        return OpenAICompatLLMProvider()
    raise ConfigurationError(f"Unsupported LLM_PROVIDER={name}")


def create_translation_provider() -> TranslationProvider:
    if settings.llm_provider == "demo":
        return DemoTranslationProvider()
    return LLMTranslationProvider(create_llm_provider())
