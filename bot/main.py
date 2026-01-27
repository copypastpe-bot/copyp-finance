import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.middlewares.db_session import DbSessionMiddleware
from bot.routers.onboarding import router as onboarding_router
from bot.routers.start import router as start_router
from core.settings_app import app_settings


async def main() -> None:
    bot = Bot(token=app_settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(start_router)
    dp.include_router(onboarding_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
