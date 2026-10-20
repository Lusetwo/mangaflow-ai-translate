from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """统一大模型调用接口：各厂商适配器只负责 complete，业务层不感知协议差异。"""

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError


class TranslationProvider(ABC):
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError
