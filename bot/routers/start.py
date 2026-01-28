from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import build_main_menu_keyboard
from bot.keyboards.onboarding import build_start_keyboard
from aiogram.fsm.context import FSMContext

from services.invite_service import InviteServiceError, get_invite_preview
from services.start_service import build_start_message
from bot.keyboards.common import build_invite_confirm_keyboard
from bot.states.onboarding import JoinBudgetStates
from services.user_service import ensure_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession, state: FSMContext) -> None:
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
                invite, budget_name, owner_username = await get_invite_preview(session, token)
                await state.update_data(invite_token=invite.token, invite_user_id=str(user.id))
                await state.set_state(JoinBudgetStates.confirm)
                owner_text = f"@{owner_username}" if owner_username else "пользователь"
                await message.answer(
                    f'{owner_text} пригласил вас в совместный бюджет "{budget_name}".',
                    reply_markup=build_invite_confirm_keyboard(),
                )
            except InviteServiceError as exc:
                await message.answer(f"Не удалось присоединиться: {exc}")
            return

    response_text = build_start_message()
    await message.answer(response_text, reply_markup=build_start_keyboard())
    await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())


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
