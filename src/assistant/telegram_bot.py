import logging
from io import BytesIO
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
        self._dp.message.register(self._on_clear_chat, Command("clear_chat"))
        self._dp.message.register(self._on_photo, F.photo)
        self._dp.message.register(self._on_text, F.text)

    async def _on_start(self, message: Message) -> None:
        await message.answer(
            "Привет! Я ИИ-преподаватель. "
            "Напиши предмет, который хочешь изучить, и цель — к какому результату идёшь. "
            "Я спрошу уровень, составлю программу и проведу занятие. "
            "Можно прислать фото по теме: конспект, задачу, схему."
        )

    async def _on_clear_chat(self, message: Message) -> None:
        self._assistant.clear(message.chat.id)
        await message.answer("История диалога очищена. Можете начать новую тему.")

    async def _on_text(self, message: Message) -> None:
        log.info("Message chat_id=%s text=%s", message.chat.id, message.text)
        answer = await self._assistant.respond(message.chat.id, message.text)
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await message.answer(answer)

    async def _on_photo(self, message: Message) -> None:
        log.info("Message chat_id=%s type=photo", message.chat.id)
        buffer = BytesIO()
        await self._bot.download(message.photo[-1], destination=buffer)
        answer = await self._assistant.respond_photo(
            message.chat.id, buffer.getvalue(), message.caption
        )
        log.info("Response chat_id=%s text=%s", message.chat.id, answer)
        await message.answer(answer)

    async def run(self) -> None:
        log.info("Polling started")
        await self._dp.start_polling(self._bot)
