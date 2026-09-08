import logging
from assistant.config import Config
from assistant.llm_client import LlmClient

log = logging.getLogger(__name__)

_ERROR_MESSAGE = "Не удалось получить ответ, попробуйте ещё раз."


class Assistant:
    def __init__(self, config: Config, llm_client: LlmClient):
        self._system_prompt = config.system_prompt
        self._llm = llm_client

    async def respond(self, text: str) -> str:
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": text},
        ]
        try:
            answer = await self._llm.complete(messages)
            return answer
        except Exception:
            log.error("LLM error", exc_info=True)
            return _ERROR_MESSAGE
