from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.onboarding import build_start_keyboard
from services.start_service import build_start_message
from services.user_service import ensure_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession) -> None:
    if message.from_user is not None:
        await ensure_user(
            session=session,
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

    response_text = build_start_message()
    await message.answer(response_text, reply_markup=build_start_keyboard())
