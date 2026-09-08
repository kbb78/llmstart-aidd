import logging
from assistant.config import Config
from assistant.llm_client import LlmClient
from assistant.chat_history import ChatHistory

log = logging.getLogger(__name__)

_ERROR_MESSAGE = "Не удалось получить ответ, попробуйте ещё раз."


class Assistant:
    def __init__(self, config: Config, llm_client: LlmClient, history: ChatHistory):
        self._system_prompt = config.system_prompt
        self._llm = llm_client
        self._history = history

    async def respond(self, chat_id: int, text: str) -> str:
        self._history.add(chat_id, "user", text)
        messages = [{"role": "system", "content": self._system_prompt}] + self._history.get(chat_id)
        try:
            answer = await self._llm.complete(messages)
            self._history.add(chat_id, "assistant", answer)
            return answer
        except Exception:
            log.error("LLM error", exc_info=True)
            self._history.remove_last(chat_id)
            return _ERROR_MESSAGE

    def clear(self, chat_id: int) -> None:
        self._history.clear(chat_id)
