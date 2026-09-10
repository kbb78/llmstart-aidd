# ADR 0014. Аудио: OpenRouter STT, `input_audio`, отдельный AudioClient

**Статус:** принято

## Контекст

Нужно принимать голосовые и аудиосообщения в Telegram и включать речь пользователя в занятие преподавателя. Telegram отдаёт файл по `file_id` (голосовые — OGG/Opus); публичного URL нет, скачать можно только с токеном бота.

OpenRouter даёт два пути «аудио → текст»:

1. **Мультимодальный chat completions** — `input_audio` или `audio_url` в `/chat/completions`. Зависит от провайдера: Nvidia Nemotron Omni не принимает `input_audio`, а для `audio_url` официально ждёт WAV/MP3/FLAC — OGG из Telegram без конвертации не распознаётся.
2. **STT** — `POST /api/v1/audio/transcriptions` (Whisper и аналоги). Тело: JSON с `input_audio` (`data` — raw base64, `format` — в т.ч. `ogg`). Клиент `openai` шлёт multipart как у OpenAI — для OpenRouter не подходит, нужен прямой HTTP JSON.

Текстовый преподаватель может работать через Ollama. URL аудио — тот же `Config.base_url`, что у текста ([ADR 0003](0003-openai-client-two-providers.md)). История — текстовые словари `{role, content}` без байтов ([ADR 0008](0008-in-memory-message-dicts.md)).

## Подходы

**Как получить текст из голоса**

| Подход | Суть | Почему нет / да |
|---|---|---|
| STT `/audio/transcriptions` + `input_audio` | Whisper и др.; `format=ogg` для голосовых Telegram | Нативная поддержка OGG; без ffmpeg; модель `AUDIO_MODEL` (например `openai/whisper-large-v3-turbo`) |
| Chat completions + `audio_url` / `input_audio` | Мультимодальная модель слушает файл | Ломается на OGG у Nvidia; конвертация через ffmpeg — лишняя зависимость в образе |
| Локальный Whisper / свой STT | Сервис или библиотека в процессе | Лишняя инфраструктура |
| Публичный URL / URL Telegram `getFile` | Провайдер качает файл сам | URL для аудио у OpenRouter нет; токен в ссылке утекает |

**Как встроить транскрипт в диалог**

| Подход | Суть | Почему нет / да |
|---|---|---|
| Один вызов: аудио сразу в `LlmClient` | Преподаватель сам слушает файл | Ollama без audio; мультимодальный `content` в истории |
| Аудио в истории | Хранить base64 / `file_id` | Раздувает память; противоречит [ADR 0008](0008-in-memory-message-dicts.md) |
| Два шага: аудио → текст → преподаватель | `AudioClient` → транскрипт → `LlmClient` | Как у фото ([ADR 0013](0013-openrouter-vision-base64.md)) |

## Решение

`TelegramBot` скачивает файл голосового или аудиосообщения и передаёт байты и формат в `Assistant`. К API провайдера хендлер не ходит.

`AudioClient` вызывает `POST {base_url}/audio/transcriptions` через `httpx` (JSON, не multipart). `base_url` — из `Config` (`LLM_BASE_URL` или таблица по `LLM_PROVIDER`). Ключ — `LLM_API_KEY`, модель — `AUDIO_MODEL`. В теле: `input_audio.data` (raw base64) и `input_audio.format` как пришло из Telegram (`ogg` для голосовых). Конвертации в WAV нет, `ffmpeg` в образе нет. На выходе — строка-транскрипт.

`AUDIO_PROMPT` остаётся в конфиге для единообразия с vision, в STT-запрос не передаётся (Whisper его не использует).

`Assistant` кладёт транскрипт в историю как реплику пользователя и вызывает `LlmClient`. Байты и base64 в историю и в лог не пишутся. TTS / ответ голосом в scope не входит.

## Следствия

Смена STT-модели — правка `AUDIO_MODEL` в `.env`. URL не зашит в код: аудио идёт туда же, куда текст. Локальный Whisper и ffmpeg не нужны. Реализация — итерация 12 в `docs/tasklist.md`.
