import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.features.budgets.router import router as budgets_router
from bot.features.main_menu.router import router as main_menu_router
from bot.features.onboarding.router import router as onboarding_router
from bot.features.settings.router import router as settings_router
from bot.middlewares.db_session import DbSessionMiddleware
from core.settings_app import app_settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=app_settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Обновить"),
            BotCommand(command="main_menu", description="Home"),
            BotCommand(command="settings", description="Настройки"),
        ]
    )

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(onboarding_router)
    dp.include_router(budgets_router)
    dp.include_router(main_menu_router)
    dp.include_router(settings_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
