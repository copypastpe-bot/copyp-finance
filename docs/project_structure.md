# Project structure — copyp-finance

Ниже описана структура репозитория и назначение ключевых файлов/папок.  
Цель документа — чтобы через 2 месяца ты открыл проект и сразу понял “что где лежит и зачем”.

---

## Корень репозитория

- **README.md**  
  Короткое описание проекта: как запустить локально/на сервере, базовые команды.

- **.gitignore**  
  Исключения из git (секреты, venv, кэш, логи).  
  Принцип: в git никогда не попадает `.env` и всё, что генерируется автоматически.

- **.env** *(не коммитится)*  
  Секреты и окружение: токен, DB доступ, режим (dev/prod), timezone и т.п.

- **requirements.txt**  
  Питон-зависимости для приложения (aiogram, sqlalchemy, alembic, asyncpg, pydantic-settings и др.).

- **Dockerfile**  
  Инструкция сборки контейнера приложения.

- **docker-compose.yml**  
  Запуск набора сервисов (сейчас — бот; позже может быть Postgres/Redis и т.д.).

---

## bot/ — Telegram слой

Назначение: “проводка” от Telegram до сервисов и обратно.  
Здесь не должно быть SQL-запросов и сложных бизнес-правил.

Типичная структура:
- **bot/main.py**  
  Точка входа: создаёт Bot/Dispatcher, подключает роутеры, запускает polling/webhook.

- **bot/routers/** *(если есть / появится)*  
  Разделение обработчиков по смыслу: users, transactions, reports.

- **bot/handlers/** *(альтернативное название routers)*  
  Содержит функции-обработчики команд и сообщений.

- **bot/middlewares/** *(по мере необходимости)*  
  Сквозные вещи: логирование, трейсинг, создание db-session на апдейт, rate-limit.

---

## services/ — бизнес-логика

Назначение: сценарии и правила предметной области, вызываемые из handlers/routers.

Типичная структура:
- **services/**  
  Модули по доменам: users, budgets, transactions, reports.

---

## core/ — инфраструктура и настройки

Назначение: общие компоненты, которые нужны везде.

Обычно тут лежит:
- **core/settings_app.py**  
  Настройки приложения (например: bot_token, app_env, log_level, tz).  
  Загружаются из `.env` через pydantic-settings.

- **core/settings_db.py**  
  Настройки базы (host/port/name/user/password).  
  Важно: `extra="ignore"` чтобы лишние переменные из `.env` не валили запуск.

- **core/logging.py** *(если появится)*  
  Конфиг логов (формат, уровень, handlers).

- **core/constants.py** *(по мере необходимости)*  
  Константы/enum’ы.

---

## db/ — слой данных (ORM)

Назначение: описание схемы БД в виде моделей и создание соединений.

Рекомендуемая структура:
- **db/base.py**  
  Базовый DeclarativeBase.  
  Почти пустой — и это нормально: он нужен как “корень” для моделей и `Base.metadata`.

- **db/models/**  
  ORM-модели (таблицы).  
  Пример: `db/models/user.py`, `db/models/transaction.py`, …

- **db/models/__init__.py**  
  Собирает импорты моделей, чтобы одним `import db.models` загрузить их все.
  Это критично для Alembic autogenerate: Alembic “видит” только то, что импортировано.

- **db/session.py** *(если добавим / уже есть)*  
  Создание async engine и async sessionmaker.

---

## migrations/ — Alembic (миграции)

Назначение: управление схемой БД через версии миграций.

- **alembic.ini** *(в корне репо)*  
  Конфиг Alembic: где скрипты, как логировать, и т.п.
  Важный параметр: `script_location = migrations`.

- **migrations/env.py**  
  “Раннер” миграций.
  - Подхватывает DB URL из settings
  - Подключает `Base.metadata`
  - Импортирует `db.models`, чтобы Alembic увидел все таблицы для autogenerate
  - Умеет offline/online режим

- **migrations/versions/**  
  Файлы миграций. Каждый файл — шаг изменения схемы.
  Пример: `xxxx_create_users.py`

- **migrations/script.py.mako**  
  Шаблон, по которому Alembic генерирует миграции.

- **migrations/README**  
  Служебный файл/заметка (можно расширять).

---

## docs/ — документация проекта

Назначение: держать “мозг проекта” в репо.

- **docs/architecture.md**  
  Архитектура: слои, потоки, принципы, варианты деплоя.

- **docs/project_structure.md** *(этот файл)*  
  Карта файлов и папок.

Дополнительно (планируется):
- **docs/ux.md** — UX-логика бота (команды/кнопки/сценарии)
- **docs/messages.md** — шаблоны сообщений (тексты ответов)
- **docs/codex_prompt.md** — промпт для Codex под разработку фич

---

## Что не должно попадать в git

- `.env` (секреты)
- `.venv/`
- `__pycache__/`
- `*.log`
- `.idea/`, `.vscode/`
- сгенерированные бинарники/кэши

Принцип: в репо только исходники и документация, всё остальное воспроизводимо установкой зависимостей и запуском команд.

---

## Минимальные рабочие команды (шпаргалка)

### Локально (в .venv)
- Активировать окружение:
  - Linux: `source .venv/bin/activate`
  - macOS: `source .venv/bin/activate`
- Миграции:
  - `alembic current`
  - `alembic heads`
  - `alembic revision --autogenerate -m "msg"`
  - `alembic upgrade head`

### Сервер (docker)
- Сборка/запуск:
  - `docker compose up -d --build`
- Логи:
  - `docker logs -f finance-bot`
- Войти в контейнер:
  - `docker exec -it finance-bot bash`
