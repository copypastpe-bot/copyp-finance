import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from core.settings_app import app_settings
token = app_settings.bot_token


async def start_handler(message: Message) -> None:
    await message.answer("Бот запущен ✅")


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
