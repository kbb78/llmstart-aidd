import base64
from openai import AsyncOpenAI
from assistant.config import Config


class VisionClient:
    def __init__(self, config: Config):
        self._client = AsyncOpenAI(
            api_key=config.llm_api_key or "ollama",
            base_url=config.base_url,
        )
        self._model = config.vision_model
        self._prompt = config.vision_prompt

    async def describe(self, image: bytes, caption: str | None = None) -> str:
        text = self._prompt
        if caption:
            text = f"{self._prompt}\n\nПодпись пользователя: {caption}"
        data_url = f"data:image/jpeg;base64,{base64.b64encode(image).decode('ascii')}"
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
        return _completion_text(response)


def _completion_text(response) -> str:
    extra = getattr(response, "model_extra", None) or {}
    error = getattr(response, "error", None) or extra.get("error")
    if not response.choices or response.choices[0].message is None:
        payload = error
        if payload is None and hasattr(response, "model_dump"):
            payload = response.model_dump()
        raise ValueError(f"Empty model response: {payload}")
    return _message_text(response.choices[0].message)


def _message_text(message) -> str:
    extra = getattr(message, "model_extra", None) or {}
    for value in (
        message.content,
        getattr(message, "reasoning", None),
        getattr(message, "reasoning_content", None),
        extra.get("reasoning"),
        extra.get("reasoning_content"),
    ):
        if isinstance(value, str) and value.strip():
            return value
    raise ValueError("Empty model response")
