from assistant.config import Config


class ChatHistory:
    def __init__(self, config: Config):
        self._limit = config.max_history_messages
        self._store: dict[int, list[dict]] = {}

    def get(self, chat_id: int) -> list[dict]:
        return list(self._store.get(chat_id, []))

    def add(self, chat_id: int, role: str, content: str) -> None:
        history = self._store.setdefault(chat_id, [])
        history.append({"role": role, "content": content})
        if len(history) > self._limit:
            del history[: len(history) - self._limit]

    def remove_last(self, chat_id: int) -> None:
        history = self._store.get(chat_id)
        if history:
            history.pop()
