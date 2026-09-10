# ADR 0003. LLM: клиент openai, два провайдера

**Статус:** принято

## Контекст

Нужен вызов чат-модели. Провайдеры: облако (OpenRouter) и локально (Ollama). Оба отдают OpenAI-совместимый HTTP API.

## Решение

Один клиент — пакет `openai`. Выбор провайдера — переменная `LLM_PROVIDER` в `.env`: `openrouter` или `ollama`. `Config` подставляет `base_url`. Ключ и имя модели — отдельные переменные окружения.

- OpenRouter: `https://openrouter.ai/api/v1`
- Ollama: `http://localhost:11434/v1`

Необязательный `LLM_BASE_URL` перекрывает URL из таблицы. Этот же `Config.base_url` используют `LlmClient`, `VisionClient` и `AudioClient`. Отдельные SDK провайдеров не используем. URL в код клиентов не вшиваем.

## Следствия

Смена провайдера — правка `LLM_PROVIDER` (и ключа/модели при необходимости) и перезапуск. Код диалога не меняется. Различия провайдеров (заголовки OpenRouter, ключ у Ollama не обязателен) закрываются в `Config`, не в `Assistant`.

При запуске в Docker дефолт Ollama `localhost:11434` указывает на контейнер. Ollama на хосте — через `LLM_BASE_URL` ([ADR 0012](0012-local-docker-compose.md)).
