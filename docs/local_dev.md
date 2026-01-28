# Локальная разработка

## 1) Подготовка окружения
1. Скопируй `.env.local.example` в `.env.local`.
2. Вставь токен тестового бота в `BOT_TOKEN`.

## 2) Поднять локальную БД
```bash
docker compose -f docker-compose.local.yml up -d db
```

## 3) Миграции
```bash
alembic upgrade head
```

## 4) Запуск бота
```bash
scripts/run_local.sh
```

## Полезные команды
Остановить БД:
```bash
docker compose -f docker-compose.local.yml down
```

Сбросить локальную БД (внимание: удалит данные):
```bash
docker compose -f docker-compose.local.yml down -v
```
