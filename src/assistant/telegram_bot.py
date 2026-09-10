import logging
from io import BytesIO
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from assistant.config import Config
from assistant.assistant import Assistant

log = logging.getLogger(__name__)

_TG_MESSAGE_LIMIT = 4096

_MIME_TO_FORMAT = {
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/flac": "flac",
    "audio/aac": "aac",
    "audio/webm": "webm",
}

_EXT_TO_FORMAT = {
    "ogg": "ogg",
    "oga": "ogg",
    "mp3": "mp3",
    "m4a": "m4a",
    "wav": "wav",
    "flac": "flac",
    "aac": "aac",
    "webm": "webm",
}


def _audio_format(message: Message) -> str:
    audio = message.audio
    if audio is None:
        return "mp3"
    if audio.mime_type:
        mapped = _MIME_TO_FORMAT.get(audio.mime_type.lower())
        if mapped:
            return mapped
    if audio.file_name and "." in audio.file_name:
        ext = audio.file_name.rsplit(".", 1)[-1].lower()
        mapped = _EXT_TO_FORMAT.get(ext)
        if mapped:
            return mapped
    return "mp3"


def _split_message(text: str, limit: int = _TG_MESSAGE_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = text.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n ")
    return chunks


class TelegramBot:
    def __init__(self, config: Config, assistant: Assistant):
        self._bot = Bot(token=config.telegram_bot_token)
        self._dp = Dispatcher()
        self._assistant = assistant
        self._dp.message.register(self._on_start, Command("start"))
        self._dp.message.register(self._on_clear_chat, Command("clear_chat"))
        self._dp.message.register(self._on_photo, F.photo)
        self._dp.message.register(self._on_voice, F.voice)
        self._dp.message.register(self._on_audio, F.audio)
        self._dp.message.register(self._on_text, F.text)

    async def _on_start(self, message: Message) -> None:
        await message.answer(
            "Привет! Я ИИ-преподаватель. "
            "Напиши предмет, который хочешь изучить, и цель — к какому результату идёшь. "
            "Я спрошу уровень, составлю программу и проведу занятие. "
            "Можно прислать фото по теме: конспект, задачу, схему. "
            "Можно прислать голос."
        )

    async def _on_clear_chat(self, message: Message) -> None:
        self._assistant.clear(message.chat.id)
        await message.answer("История диалога очищена. Можете начать новую тему.")

    async def _answer(self, message: Message, text: str) -> None:
        for chunk in _split_message(text):
            await message.answer(chunk)

    async def _on_text(self, message: Message) -> None:
        log.info("Message chat_id=%s text=%s", message.chat.id, message.text)
        answer = await self._assistant.respond(message.chat.id, message.text)
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await self._answer(message, answer)

    async def _on_photo(self, message: Message) -> None:
        log.info("Message chat_id=%s type=photo", message.chat.id)
        buffer = BytesIO()
        await self._bot.download(message.photo[-1], destination=buffer)
        answer = await self._assistant.respond_photo(
            message.chat.id, buffer.getvalue(), message.caption
        )
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await self._answer(message, answer)

    async def _on_voice(self, message: Message) -> None:
        log.info("Message chat_id=%s type=voice", message.chat.id)
        buffer = BytesIO()
        await self._bot.download(message.voice, destination=buffer)
        answer = await self._assistant.respond_audio(
            message.chat.id, buffer.getvalue(), "ogg"
        )
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await self._answer(message, answer)

    async def _on_audio(self, message: Message) -> None:
        log.info("Message chat_id=%s type=audio", message.chat.id)
        buffer = BytesIO()
        await self._bot.download(message.audio, destination=buffer)
        answer = await self._assistant.respond_audio(
            message.chat.id, buffer.getvalue(), _audio_format(message)
        )
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await self._answer(message, answer)

    async def run(self) -> None:
        log.info("Polling started")
        await self._dp.start_polling(self._bot)
