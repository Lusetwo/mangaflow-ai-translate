from abc import ABC, abstractmethod
from typing import Sequence


class LLMProvider(ABC):
    """统一大模型调用接口：各厂商适配器只负责 complete，业务层不感知协议差异。"""

    @abstractmethod
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """单轮补全；system_prompt 非空时作为 messages[0] 的 system role。"""
        raise NotImplementedError


class TranslationProvider(ABC):
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError

    async def translate_batch(self, texts: Sequence[str], source_lang: str, target_lang: str) -> list[str]:
        """批量翻译的默认实现：逐条串行调用。子类可覆盖为一次 LLM 请求。"""
        return [await self.translate(t, source_lang, target_lang) for t in texts]
