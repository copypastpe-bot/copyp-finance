# DB schema v1 — copyp-finance

Этот документ определяет **базовую** схему PostgreSQL для copyp-finance.
Это источник истины для инвариантов БД и ORM-маппинга.

## Цели схемы
- Мультипользовательский режим, несколько бюджетов.
- Валюты бюджета: **1 базовая + до 2 вспомогательных**.
- Операции (transactions): доход/расход/движения по копилкам с:
  - исходной суммой и валютой
  - пересчитанной суммой в базовой валюте бюджета для агрегаций
  - монотонным `seq_no` **в рамках бюджета**
  - soft delete
  - возможностью редактирования с аудитом
- Категории общие внутри бюджета; персональная сортировка категорий — по пользователю.
- Копилки (goals): общие и личные (личные видны только владельцу копилки).

## Конвенции
- Все временные метки — `timestamptz` (UTC).
- Денежные значения — `numeric(14, 2)`, если не указано иное.
- Валюта хранится как ISO-4217 код из 3 символов (`char(3)`), в верхнем регистре.
- Первичные ключи: `uuid`.

---

## ER-обзор

### Users
Телеграм-идентичность пользователя.

### Budgets
Бюджет со своей базовой валютой и таймзоной; может иметь несколько участников.

### Memberships
Ролевой доступ на уровне бюджета.

### Categories
Общие категории внутри бюджета.

### Goals
Копилки (цели накоплений) внутри бюджета; могут быть общими или личными.

### Transactions
Доходы/расходы плюс движения по копилкам. Каждая операция принадлежит ровно одному бюджету.

### Transaction audit
Неизменяемая история редактирований операций.

---

## Таблицы

### 1) `users`
Представляет пользователя Telegram.

Колонки:
- `id` uuid PK
- `telegram_user_id` bigint UNIQUE NOT NULL
- `telegram_username` text NULL
- `first_name` text NULL
- `last_name` text NULL
- `active_budget_id` uuid NULL FK → `budgets.id`
- `created_at` timestamptz NOT NULL DEFAULT now()

Индексы/ограничения:
- `uq_users_telegram_user_id (telegram_user_id)`

---

### 2) `budgets`
Представляет бюджет (кошелёк).

Колонки:
- `id` uuid PK
- `name` text NOT NULL
- `base_currency` char(3) NOT NULL
- `aux_currency_1` char(3) NULL
- `aux_currency_2` char(3) NULL
- `timezone` text NOT NULL  (IANA-имя, например `Europe/Belgrade`)
- `created_by_user_id` uuid NOT NULL FK → `users.id`
- `created_at` timestamptz NOT NULL DEFAULT now()
- `is_archived` boolean NOT NULL DEFAULT false

Ограничения:
- `chk_budget_aux_distinct`: вспомогательные валюты должны отличаться от базовой и друг от друга (если не NULL).

Индексы:
- `idx_budgets_created_by_user_id`

---

### 3) `budget_memberships`
Участники бюджета.

Колонки:
- `id` uuid PK
- `budget_id` uuid NOT NULL FK → `budgets.id`
- `user_id` uuid NOT NULL FK → `users.id`
- `role` text NOT NULL  (enum-like: `owner`, `participant`)
- `joined_at` timestamptz NOT NULL DEFAULT now()
- `is_active` boolean NOT NULL DEFAULT true

Ограничения:
- `uq_budget_memberships_budget_user (budget_id, user_id)`

Индексы:
- `idx_budget_memberships_budget_id`
- `idx_budget_memberships_user_id`

Примечания:
- “Ровно один owner на бюджет” фиксируем в прикладной логике (services). При необходимости позже можно усилить частичным уникальным индексом.

---

### 4) `budget_counters`
Счётчики на уровне бюджета для безопасной выдачи `seq_no` при конкурентных вставках.

Колонки:
- `budget_id` uuid PK FK → `budgets.id`
- `next_seq_no` integer NOT NULL DEFAULT 1
- `updated_at` timestamptz NOT NULL DEFAULT now()

Алгоритм аллокации (на уровне сервиса):
- `SELECT next_seq_no FROM budget_counters WHERE budget_id=:id FOR UPDATE;`
- полученное значение используем как `seq_no`
- `UPDATE budget_counters SET next_seq_no = next_seq_no + 1, updated_at=now() ...`

---

### 5) `categories`
Общий справочник категорий внутри бюджета.

Колонки:
- `id` uuid PK
- `budget_id` uuid NOT NULL FK → `budgets.id`
- `name` text NOT NULL
- `kind` text NOT NULL  (enum-like: `income`, `expense`, `both`)
- `created_at` timestamptz NOT NULL DEFAULT now()
- `is_active` boolean NOT NULL DEFAULT true

Ограничения:
- `uq_categories_budget_name_kind (budget_id, name, kind)` (опционально; если допускаем одинаковое имя отдельно для доходов/расходов — оставляем `kind` в ключе)

Индексы:
- `idx_categories_budget_id`

---

### 6) `user_category_stats`
Метаданные использования категорий для персональной сортировки.

Колонки:
- `id` uuid PK
- `user_id` uuid NOT NULL FK → `users.id`
- `category_id` uuid NOT NULL FK → `categories.id`
- `usage_count` integer NOT NULL DEFAULT 0
- `last_used_at` timestamptz NULL

Ограничения:
- `uq_user_category_stats_user_category (user_id, category_id)`

Индексы:
- `idx_user_category_stats_user_id`

---

### 7) `goals`
Копилки (цели накоплений) внутри бюджета.

Колонки:
- `id` uuid PK
- `budget_id` uuid NOT NULL FK → `budgets.id`
- `owner_user_id` uuid NOT NULL FK → `users.id`  (владелец копилки)
- `visibility` text NOT NULL (enum-like: `shared`, `private`)
- `name` text NOT NULL
- `target_amount_base` numeric(14,2) NULL
- `note` text NULL
- `created_at` timestamptz NOT NULL DEFAULT now()
- `is_archived` boolean NOT NULL DEFAULT false

Индексы:
- `idx_goals_budget_id`
- `idx_goals_owner_user_id`

Инвариант приватности:
- Если `visibility='private'`, только `owner_user_id` имеет право читать/писать копилку и связанные с ней операции.

---

### 8) `transactions`
Все движения денег: доходы, расходы и движения по копилкам.

Колонки:
- `id` uuid PK
- `budget_id` uuid NOT NULL FK → `budgets.id`
- `seq_no` integer NOT NULL  (монотонный номер операции в рамках бюджета)
- `type` text NOT NULL (enum-like: `income`, `expense`, `goal_deposit`, `goal_withdraw`)
- `amount` numeric(14,2) NOT NULL          (исходная сумма)
- `currency` char(3) NOT NULL              (исходная валюта)
- `amount_base` numeric(14,2) NOT NULL     (сумма в базовой валюте бюджета)
- `fx_rate` numeric(18,8) NOT NULL         (курс пересчёта)
- `fx_date` date NOT NULL                  (дата курса)
- `occurred_at` timestamptz NOT NULL       (момент операции в UTC)
- `local_date` date NOT NULL               (дата по таймзоне бюджета — для быстрых агрегаций по дням/месяцам)
- `category_id` uuid NULL FK → `categories.id`
- `goal_id` uuid NULL FK → `goals.id`
- `comment` text NULL

Атрибуция:
- `created_by_user_id` uuid NOT NULL FK → `users.id`
- `created_at` timestamptz NOT NULL DEFAULT now()
- `updated_by_user_id` uuid NULL FK → `users.id`
- `updated_at` timestamptz NULL

Soft delete:
- `is_deleted` boolean NOT NULL DEFAULT false
- `deleted_by_user_id` uuid NULL FK → `users.id`
- `deleted_at` timestamptz NULL

AI / источник ввода (опционально, но полезно для дебага):
- `input_type` text NULL (enum-like: `text`, `voice`, `photo`, `document`)
- `telegram_file_id` text NULL
- `raw_text` text NULL           (на уровне приложения ограничиваем размер и при необходимости обрезаем)
- `parsed_payload` jsonb NULL    (структурированный результат парсинга)

Ограничения:
- `uq_transactions_budget_seq_no (budget_id, seq_no)`
- `chk_transactions_goal_type`: если `type` — `goal_deposit` или `goal_withdraw`, то `goal_id` должен быть NOT NULL; иначе `goal_id` должен быть NULL.

Индексы:
- `idx_transactions_budget_id_local_date`
- `idx_transactions_budget_id_occurred_at`
- `idx_transactions_created_by_user_id`
- `idx_transactions_category_id`

Примечания:
- Все отчёты должны по умолчанию фильтровать `is_deleted=false`.
- Редактирование операций допускается, но обязателен аудит.

---

### 9) `transaction_audit`
Неизменяемый журнал редактирований операций.

Колонки:
- `id` uuid PK
- `transaction_id` uuid NOT NULL FK → `transactions.id`
- `edited_at` timestamptz NOT NULL DEFAULT now()
- `edited_by_user_id` uuid NOT NULL FK → `users.id`
- `before` jsonb NOT NULL
- `after` jsonb NOT NULL
- `reason` text NULL

Индексы:
- `idx_transaction_audit_transaction_id`
- `idx_transaction_audit_edited_by_user_id`

---

### 10) `budget_invites`
Инвайты для присоединения к бюджету.

Колонки:
- `id` uuid PK
- `budget_id` uuid NOT NULL FK → `budgets.id`
- `token` text NOT NULL (уникальный токен)
- `created_by_user_id` uuid NOT NULL FK → `users.id`
- `created_at` timestamptz NOT NULL DEFAULT now()
- `expires_at` timestamptz NOT NULL
- `max_uses` integer NOT NULL DEFAULT 1
- `used_count` integer NOT NULL DEFAULT 0
- `last_used_at` timestamptz NULL
- `is_active` boolean NOT NULL DEFAULT true

Индексы:
- `ux_budget_invites_token` (unique)
- `idx_budget_invites_budget_id`
- `idx_budget_invites_created_by_user_id`

Правила:
- Инвайт одноразовый (`max_uses=1`).
- Срок действия — 24 часа от момента создания.
- Просроченный или использованный инвайт не действует.

---

## Enum definitions (logical)
В v1 это “enum-like” текстовые поля. Позже можно мигрировать на PostgreSQL ENUM.

- `budget_memberships.role`: `owner` | `participant`
- `categories.kind`: `income` | `expense` | `both`
- `goals.visibility`: `shared` | `private`
- `transactions.type`: `income` | `expense` | `goal_deposit` | `goal_withdraw`
- `transactions.input_type`: `text` | `voice` | `photo` | `document`

---

## Правила на уровне сервисов (зависят от схемы)

1. **Правила участия**
   - Пользователь взаимодействует с бюджетом только если membership `is_active=true`.
   - Только `owner` может: создавать бюджеты, управлять участниками, удалять операции, создавать общие копилки.
   - `participant` может: создавать операции и смотреть сводки/отчёты.
   - `participant` может создавать личные копилки; личные копилки невидимы другим участникам, включая owner бюджета.

2. **Окно редактирования**
   - По умолчанию редактирование разрешено только в пределах той же `local_date`, что и операция (таймзона бюджета).
   - При каждом редактировании: вставлять запись в `transaction_audit` с before/after снимками.

3. **Пересчёт валют (FX)**
   - Если валюта операции равна базовой валюте бюджета: `amount_base=amount`, `fx_rate=1`, `fx_date=local_date`.
   - Иначе: получить курс на `fx_date` (обычно `local_date` операции) и сохранить использованный курс.

4. **Выдача `seq_no`**
   - Выдавать `seq_no` через `budget_counters` с блокировкой строки (row-level lock).

---

## Чек-лист реализации (ORM + migrations)
- Создать SQLAlchemy-модели, отражающие таблицы выше.
- Убедиться, что `db/models/__init__.py` импортирует все модели для Alembic autogenerate.
- Добавить Alembic миграцию `0001_init_schema`.
- Добавить ограничения (distinct currencies, goal-type rule, unique keys, indexes).
