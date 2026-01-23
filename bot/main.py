import asyncio

from aiogram import Bot, Dispatcher

from bot.routers.start import router as start_router
from core.settings_app import app_settings


async def main() -> None:
    bot = Bot(token=app_settings.bot_token)
    dp = Dispatcher()

    dp.include_router(start_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
