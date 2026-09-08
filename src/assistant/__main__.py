import logging
from assistant.config import Config

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)


def main():
    config = Config()
    logging.getLogger().setLevel(config.log_level)
    log.info("Starting: provider=%s model=%s", config.llm_provider, config.llm_model)
    # iteration 3: запуск TelegramBot


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error("Startup failed: %s", e)
        raise SystemExit(1)
