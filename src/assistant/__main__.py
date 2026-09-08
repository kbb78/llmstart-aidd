import asyncio
import logging
from assistant.config import Config
from assistant.telegram_bot import TelegramBot

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)


async def main():
    config = Config()
    logging.getLogger().setLevel(config.log_level)
    log.info("Starting: provider=%s model=%s", config.llm_provider, config.llm_model)
    bot = TelegramBot(config)
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log.error("Startup failed: %s", e)
        raise SystemExit(1)
