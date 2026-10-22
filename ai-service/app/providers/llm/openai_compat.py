import httpx
from app.core.config import settings
from app.core.exceptions import ConfigurationError, ProviderError
from app.providers.llm.base import LLMProvider

_PRESETS = {
    "deepseek": ("https://api.deepseek.com", "deepseek-chat"),
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini"),
    "openai_compat": ("", ""),
}


"""OpenAI Chat Completions 兼容客户端：DeepSeek / OpenAI / 其它兼容网关均可复用。"""
class OpenAICompatLLMProvider(LLMProvider):
    def __init__(self):
        preset_base, preset_model = _PRESETS.get(settings.llm_provider, ("", ""))
        self.api_key = settings.llm_api_key
        self.base_url = (settings.llm_base_url or preset_base).rstrip("/")
        self.model = settings.llm_model or preset_model
        self.timeout = settings.llm_timeout_seconds
        self.proxy = settings.llm_http_proxy
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            client_kwargs: dict = {"timeout": self.timeout}
            if self.proxy:
                client_kwargs["proxy"] = self.proxy
            self._client = httpx.AsyncClient(**client_kwargs)
        return self._client

    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if not self.api_key:
            raise ConfigurationError(f"LLM_PROVIDER={settings.llm_provider} requires LLM_API_KEY")
        if not self.base_url or not self.model:
            raise ConfigurationError(f"LLM_PROVIDER={settings.llm_provider} requires LLM_BASE_URL and LLM_MODEL")
        url = f"{self.base_url}/chat/completions"
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = await self._get_client().post(url, headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }, json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
            })
            response.raise_for_status()
            data = response.json()
            return self._extract_text(data)
        except ConfigurationError:
            raise
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"LLM request failed: {self._http_error_detail(exc)}") from exc
        except httpx.RequestError as exc:
            hint = "network unreachable; set LLM_HTTP_PROXY if needed" if isinstance(exc, httpx.ConnectError) else str(exc)
            raise ProviderError(f"LLM request failed: {hint}") from exc
        except Exception as exc:
            raise ProviderError(f"LLM request failed: {exc}") from exc

    @staticmethod
    def _extract_text(data: dict) -> str:
        choices = data.get("choices") or []
        if not choices:
            raise ProviderError("LLM returned no choices")
        message = (choices[0] or {}).get("message") or {}
        text = str(message.get("content") or "").strip()
        if not text:
            raise ProviderError("LLM returned empty content")
        return text

    @staticmethod
    def _http_error_detail(exc: httpx.HTTPStatusError) -> str:
        status = exc.response.status_code
        try:
            payload = exc.response.json()
            error = payload.get("error")
            if isinstance(error, dict):
                message = str(error.get("message") or "").strip()
            else:
                message = str(error or payload.get("message") or "").strip()
            if message:
                return f"HTTP {status}: {message}"
        except Exception:
            pass
        body = (exc.response.text or "").strip()
        return f"HTTP {status}: {body[:300]}" if body else f"HTTP {status}"
