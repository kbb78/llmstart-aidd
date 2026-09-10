import base64
import httpx
from assistant.config import Config


class AudioClient:
    def __init__(self, config: Config):
        self._api_key = config.llm_api_key or "ollama"
        self._model = config.audio_model
        self._base_url = config.base_url

    async def transcribe(self, audio: bytes, format: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "input_audio": {
                        "data": base64.b64encode(audio).decode("ascii"),
                        "format": format,
                    },
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Empty transcription: {payload}")
        return text.strip()
