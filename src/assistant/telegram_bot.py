import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from assistant.config import Config

log = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, config: Config):
        self._bot = Bot(token=config.telegram_bot_token)
        self._dp = Dispatcher()
        self._dp.message.register(self._on_start, Command("start"))

    async def _on_start(self, message: Message) -> None:
        await message.answer("Привет! Напиши мне что-нибудь.")

    async def run(self) -> None:
        log.info("Polling started")
        await self._dp.start_polling(self._bot)
