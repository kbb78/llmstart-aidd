import logging
from openai import AsyncOpenAI
from assistant.config import Config

log = logging.getLogger(__name__)


class LlmClient:
    def __init__(self, config: Config):
        api_key = config.llm_api_key or "ollama"
        self._client = AsyncOpenAI(api_key=api_key, base_url=config.base_url)
        self._model = config.llm_model
        self._max_tokens = config.llm_max_tokens

    async def complete(self, messages: list[dict]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=self._max_tokens,
        )
        return _completion_text(response)


def _completion_text(response) -> str:
    extra = getattr(response, "model_extra", None) or {}
    error = getattr(response, "error", None) or extra.get("error")
    if not response.choices or response.choices[0].message is None:
        payload = error
        if payload is None and hasattr(response, "model_dump"):
            payload = response.model_dump()
        raise ValueError(f"Empty model response: {payload}")
    return _message_text(response.choices[0].message)


def _message_text(message) -> str:
    content = message.content
    if isinstance(content, str) and content.strip():
        return content
    raise ValueError("Empty model response")
