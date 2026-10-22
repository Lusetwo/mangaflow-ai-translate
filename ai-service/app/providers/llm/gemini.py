import httpx
from app.core.config import settings
from app.core.exceptions import ConfigurationError, ProviderError
from app.providers.llm.base import LLMProvider

_DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta"
_DEFAULT_MODEL = "gemini-3.8-flash"


"""Gemini generateContent 适配器：实现统一 LLMProvider.complete。"""
class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.base_url = (settings.llm_base_url or _DEFAULT_BASE).rstrip("/")
        self.model = settings.llm_model or _DEFAULT_MODEL
        self.timeout = settings.llm_timeout_seconds
        self.proxy = settings.llm_http_proxy

    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if not self.api_key:
            raise ConfigurationError("LLM_PROVIDER=gemini requires LLM_API_KEY")
        url = f"{self.base_url}/models/{self.model}:generateContent"
        client_kwargs: dict = {"timeout": self.timeout}
        if self.proxy:
            client_kwargs["proxy"] = self.proxy
        body: dict = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        try:
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(url, params={"key": self.api_key}, json=body)
                response.raise_for_status()
                return self._extract_text(response.json())
        except ConfigurationError:
            raise
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"Gemini request failed: {self._http_error_detail(exc)}") from exc
        except httpx.RequestError as exc:
            hint = (
                "network unreachable; set LLM_HTTP_PROXY (e.g. http://127.0.0.1:7897)"
                if isinstance(exc, httpx.ConnectError) else str(exc)
            )
            raise ProviderError(f"Gemini request failed: {hint}") from exc
        except Exception as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc

    @staticmethod
    def _extract_text(data: dict) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            raise ProviderError("Gemini returned no candidates")
        parts = (((candidates[0] or {}).get("content") or {}).get("parts")) or []
        texts = [str(part.get("text", "")).strip() for part in parts if part.get("text")]
        if not texts:
            raise ProviderError("Gemini returned empty content")
        return "\n".join(texts).strip()

    @staticmethod
    def _http_error_detail(exc: httpx.HTTPStatusError) -> str:
        status = exc.response.status_code
        try:
            payload = exc.response.json()
            message = (((payload.get("error") or {}).get("message")) or "").strip()
            if message:
                return f"HTTP {status}: {message}"
        except Exception:
            pass
        body = (exc.response.text or "").strip()
        return f"HTTP {status}: {body[:300]}" if body else f"HTTP {status}"
