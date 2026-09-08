# ADR 0001. Python, uv, Make

**Статус:** принято

## Контекст

Нужен минимальный стек для проверки идеи Telegram-бота с LLM. Запуск — локально в Docker (см. [ADR 0012](0012-local-docker-compose.md)).

## Решение

- Язык: Python 3.12+.
- Зависимости и окружение: `uv`, манифест `pyproject.toml`, lock-файл `uv.lock` в git. `uv sync` выполняется в образе при сборке.
- Пользовательские команды: `make` как обёртка над `docker compose` (`build`, `run`, `up`, `down`, `logs`).

## Следствия

Один источник зависимостей — `pyproject.toml`. `requirements.txt` не ведём. Make не дублирует логику сборки: только вызывает Compose.
