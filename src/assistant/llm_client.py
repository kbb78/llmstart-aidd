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
        return response.choices[0].message.content
