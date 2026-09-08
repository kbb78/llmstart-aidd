# ADR 0012. Локальный запуск через Docker Compose

**Статус:** принято

Заменяет [ADR 0011](0011-local-make-background.md).

## Контекст

Первая версия должна запускаться на своей машине. Фон через `nohup`/`screen` неудобен (особенно на Windows) и плохо стыкуется с воспроизводимым окружением. Нужен один способ: передний план и фон.

## Решение

Запуск — локальный Docker Compose. Образ собирается из `Dockerfile`: Python 3.12, зависимости ставит `uv` по `pyproject.toml` и `uv.lock`. Команды пользователя — цели Make над `docker compose`.

- Передний план: `make run` (`docker compose up`), остановка Ctrl+C.
- Фон: `make up` (`docker compose up -d`), логи `make logs`, остановка `make down`.
- `.env` передаётся в контейнер через Compose. Отдельных скриптов `nohup`/`screen` нет.

`localhost` внутри контейнера — не хост. Для Ollama на машине задаётся `LLM_BASE_URL` (например `http://host.docker.internal:11434/v1`). В Compose при необходимости добавляется `extra_hosts: host.docker.internal:host-gateway` (Linux).

CI, облако, systemd не входят в первую версию.

## Следствия

Окружение воспроизводится образом. Рестарт контейнера очищает историю в памяти. Доступ к Ollama на хосте — только через `LLM_BASE_URL`, дефолт `localhost:11434` из контейнера не работает.
