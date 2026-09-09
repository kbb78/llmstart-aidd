# LLMSTART-AIDD — Telegram-бот «ИИ-преподаватель»

Telegram-бот — ИИ-наставник по выбранному предмету или навыку. Ведёт полный цикл обучения: выясняет цель и уровень, составляет программу, объясняет, даёт практику, проверяет ответы и подстраивает сложность. Не отвечает на один вопрос и не закрывает тему.

## Возможности

- **Предмет и цель** — пользователь выбирает, чему учиться и к какому результату идёт
- **Программа** — бот составляет план занятий под цель и уровень
- **Объяснение** — разбирает тему простым языком с примерами, затем переходит к практике
- **Задания и проверка** — даёт упражнения, разбирает ответ и указывает, как исправить ошибки
- **Адаптация** — упрощает или усложняет материал по результатам
- **Прогресс** — помнит пройденное в рамках истории диалога и продолжает с этого места
- **Настраиваемая роль** — роль задаётся через `SYSTEM_PROMPT` в `.env` без изменения кода
- **Лимит ответа** — длина ответа модели ограничена `LLM_MAX_TOKENS` (по умолчанию 2000 токенов)

## Технологический стек

| Слой | Выбор |
|---|---|
| Язык | Python 3.12+ |
| Зависимости | `uv`, `pyproject.toml` |
| Telegram | aiogram 3, long polling |
| LLM | клиент `openai` (OpenAI-совместимый API) |
| Провайдеры LLM | OpenRouter, Ollama |
| Контейнеризация | Docker, Docker Compose |
| Облако | Railway |
| Конфиг | переменные окружения, `.env` |

## Архитектура

Один процесс, объекты собираются вручную в `__main__.py`. Поток сообщения:

```mermaid
flowchart TD
    User([Пользователь])
    TG[Telegram]
    Bot[TelegramBot]
    Asst[Assistant]
    Hist[ChatHistory]
    LLM_C[LlmClient]
    LLM_API[("LLM API\nOpenRouter / Ollama")]
    Cfg[Config]

    User -- текст --> TG
    TG -- "текст + chat_id" --> Bot
    Bot -- respond --> Asst
    Asst -- "запись user" --> Hist
    Hist -- история --> Asst
    Asst -- "system_prompt + история" --> LLM_C
    LLM_C -- chat completions --> LLM_API
    LLM_API -- ответ --> LLM_C
    LLM_C -- текст --> Asst
    Asst -- "запись assistant" --> Hist
    Asst -- ответ --> Bot
    Bot -- send_message --> TG
    TG -- ответ --> User

    Cfg -. токен, модель, промпт .-> Bot
    Cfg -. base_url, ключ, модель, max_tokens .-> LLM_C
    Cfg -. лимит истории .-> Hist
```

## Быстрый старт (локально)

### Требования

- Docker и Docker Compose
- Токен Telegram-бота ([получить у @BotFather](https://t.me/BotFather))
- API-ключ OpenRouter (или локальная Ollama)

### Установка

```bash
git clone <repo-url>
cd llmstart-aidd
cp .env.example .env
```

Заполните `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4o-mini
LLM_API_KEY=your_openrouter_key
LLM_MAX_TOKENS=2000
SYSTEM_PROMPT=Ты — ИИ-преподаватель...
```

### Запуск

```bash
make build   # собрать образ
make run     # запустить на переднем плане (Ctrl+C для остановки)
make up      # запустить в фоне
make logs    # смотреть логи
make down    # остановить
```

## Деплой в Railway

1. Подключите репозиторий на [railway.app](https://railway.app/new)
2. В разделе **Variables** задайте те же переменные, что и в `.env`
3. Railway автоматически соберёт Docker-образ и запустит бота

Long polling работает в облаке без изменений — публичный URL не нужен.

## Демонстрация

<!-- Добавьте скриншот или GIF с работой бота -->
![Demo](docs/assistant_demo.gif)
> _Скриншот или GIF появится здесь_
