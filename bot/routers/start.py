from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.onboarding import build_start_keyboard
from services.invite_service import InviteServiceError, accept_invite
from services.start_service import build_start_message
from services.user_service import ensure_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession) -> None:
    if message.from_user is not None:
        user = await ensure_user(
            session=session,
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

        token = _extract_invite_token(message.text or "")
        if token is not None:
            try:
                await accept_invite(session, token, user.id)
                await message.answer("✅ Ты присоединился к бюджету.")
            except InviteServiceError as exc:
                await message.answer(f"Не удалось присоединиться: {exc}")

    response_text = build_start_message()
    await message.answer(response_text, reply_markup=build_start_keyboard())


def _extract_invite_token(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None
    if "start=invite_" in text:
        return text.split("start=invite_", 1)[1].strip()
    if text.startswith("/start "):
        payload = text.split(" ", 1)[1].strip()
        if payload.startswith("invite_"):
            return payload.replace("invite_", "", 1).strip()
    return None
