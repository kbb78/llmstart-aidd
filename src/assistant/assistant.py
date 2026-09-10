import logging
from assistant.config import Config
from assistant.llm_client import LlmClient
from assistant.chat_history import ChatHistory
from assistant.vision_client import VisionClient
from assistant.audio_client import AudioClient

log = logging.getLogger(__name__)

_ERROR_MESSAGE = "Не удалось получить ответ, попробуйте ещё раз."


class Assistant:
    def __init__(
        self,
        config: Config,
        llm_client: LlmClient,
        history: ChatHistory,
        vision_client: VisionClient,
        audio_client: AudioClient,
    ):
        self._system_prompt = config.system_prompt
        self._llm = llm_client
        self._history = history
        self._vision = vision_client
        self._audio = audio_client

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

    async def respond_photo(self, chat_id: int, image: bytes, caption: str | None) -> str:
        try:
            description = await self._vision.describe(image, caption)
        except Exception:
            log.error("Vision error", exc_info=True)
            return _ERROR_MESSAGE
        log.info("Vision chat_id=%s text=%s", chat_id, description)
        if caption:
            user_text = (
                f"Пользователь прислал фото с подписью: {caption}\n\n"
                f"Описание снимка: {description}"
            )
        else:
            user_text = (
                f"Пользователь прислал фото.\n\n"
                f"Описание снимка: {description}"
            )
        return await self.respond(chat_id, user_text)

    async def respond_audio(self, chat_id: int, audio: bytes, format: str) -> str:
        try:
            transcript = await self._audio.transcribe(audio, format)
        except Exception:
            log.error("Audio error", exc_info=True)
            return _ERROR_MESSAGE
        log.info("Audio chat_id=%s text=%s", chat_id, transcript)
        user_text = (
            f"Пользователь прислал голосовое сообщение.\n\n"
            f"Транскрипт: {transcript}"
        )
        return await self.respond(chat_id, user_text)

    def clear(self, chat_id: int) -> None:
        self._history.clear(chat_id)
