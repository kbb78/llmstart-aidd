import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.telegram_bot_token = self._require("TELEGRAM_BOT_TOKEN")
        self.llm_provider = self._require("LLM_PROVIDER")
        if self.llm_provider not in ("openrouter", "ollama"):
            raise ValueError(f"Unknown LLM_PROVIDER: {self.llm_provider}")
        self.llm_model = self._require("LLM_MODEL")
        self.system_prompt = self._require("SYSTEM_PROMPT")
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_base_url = os.getenv("LLM_BASE_URL")
        self.max_history_messages = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def _require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required env var: {name}")
        return value

    @property
    def base_url(self) -> str:
        if self.llm_base_url:
            return self.llm_base_url
        return {
            "openrouter": "https://openrouter.ai/api/v1",
            "ollama": "http://localhost:11434/v1",
        }[self.llm_provider]
