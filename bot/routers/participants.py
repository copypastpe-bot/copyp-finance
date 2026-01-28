import uuid

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.participants import build_confirm_remove_keyboard, build_participants_keyboard
from services.participants_service import (
    ParticipantsServiceError,
    get_participant_display,
    list_active_participants,
    remove_participant,
)
from services.user_service import ensure_user

router = Router()


@router.callback_query(F.data == "participants:list")
async def participants_list(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    try:
        items = await list_active_participants(session, user.id)
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось открыть участников: {exc}")
        await _safe_callback_answer(callback)
        return

    if not items:
        await callback.message.answer("Участников нет.")
        await _safe_callback_answer(callback)
        return

    lines = ["👥 Участники\n"]
    participant_ids: list[str] = []
    for item in items:
        lines.append(f"{item['username']} — {item['name']} ({item['role']})")
        if item["role"] != "владелец":
            participant_ids.append(item["user_id"])

    text = "\n".join(lines)
    await callback.message.answer(text, reply_markup=build_participants_keyboard(participant_ids))
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("participants:remove:"))
async def participants_remove(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    participant_id = callback.data.split("participants:remove:", 1)[1]
    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    try:
        display = await get_participant_display(
            session, user.id, uuid.UUID(participant_id)
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer(
        f"Удалить участника?\n{display}",
        reply_markup=build_confirm_remove_keyboard(participant_id),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("participants:confirm:"))
async def participants_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    participant_id = callback.data.split("participants:confirm:", 1)[1]
    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    try:
        await remove_participant(
            session,
            user.id,
            uuid.UUID(participant_id),
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer("✅ Участник удалён.")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "participants:close")
async def participants_close(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "participants:cancel")
async def participants_cancel(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return
