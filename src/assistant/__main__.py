import asyncio
import logging
from assistant.config import Config
from assistant.llm_client import LlmClient
from assistant.chat_history import ChatHistory
from assistant.vision_client import VisionClient
from assistant.audio_client import AudioClient
from assistant.assistant import Assistant
from assistant.telegram_bot import TelegramBot

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)


async def main():
    config = Config()
    logging.getLogger().setLevel(config.log_level)
    log.info(
        "Starting: provider=%s model=%s vision_model=%s audio_model=%s",
        config.llm_provider,
        config.llm_model,
        config.vision_model,
        config.audio_model,
    )
    llm_client = LlmClient(config)
    history = ChatHistory(config)
    vision_client = VisionClient(config)
    audio_client = AudioClient(config)
    assistant = Assistant(config, llm_client, history, vision_client, audio_client)
    bot = TelegramBot(config, assistant)
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log.error("Startup failed: %s", e)
        raise SystemExit(1)
