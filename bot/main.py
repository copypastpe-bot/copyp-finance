import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from bot.middlewares.db_session import DbSessionMiddleware
from bot.routers.main_menu import router as main_menu_router
from bot.routers.onboarding import router as onboarding_router
from bot.routers.participants import router as participants_router
from bot.routers.budgets import router as budgets_router
from bot.routers.start import router as start_router
from core.settings_app import app_settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=app_settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    await bot.set_my_commands([BotCommand(command="start", description="Запуск бота")])

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(start_router)
    dp.include_router(onboarding_router)
    dp.include_router(participants_router)
    dp.include_router(budgets_router)
    dp.include_router(main_menu_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
