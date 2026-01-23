from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.start_service import build_start_message

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    response_text = build_start_message()
    await message.answer(response_text)
