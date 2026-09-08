import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from assistant.config import Config
from assistant.assistant import Assistant

log = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, config: Config, assistant: Assistant):
        self._bot = Bot(token=config.telegram_bot_token)
        self._dp = Dispatcher()
        self._assistant = assistant
        self._dp.message.register(self._on_start, Command("start"))
        self._dp.message.register(self._on_text, F.text)

    async def _on_start(self, message: Message) -> None:
        await message.answer(
            "Привет! Я твой онлайн-преподаватель. "
            "Напиши тему, которую хочешь изучить, и я объясню её с примерами."
        )

    async def _on_text(self, message: Message) -> None:
        log.info("Message chat_id=%s text=%s", message.chat.id, message.text)
        answer = await self._assistant.respond(message.chat.id, message.text)
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await message.answer(answer)

    async def run(self) -> None:
        log.info("Polling started")
        await self._dp.start_polling(self._bot)
