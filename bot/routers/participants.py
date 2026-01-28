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
from bot.utils.callback_data import decode_uuid

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
    keyboard_items: list[dict[str, str]] = []
    for item in items:
        lines.append(f"{item['username']} — {item['name']} ({item['role']})")
        if item["role"] != "владелец":
            keyboard_items.append(
                {"user_id": item["user_id"], "username": item["username"]}
            )

    text = "\n".join(lines)
    await callback.message.answer(
        text, reply_markup=build_participants_keyboard(keyboard_items, None, None)
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("p:rm:"))
async def participants_remove(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    payload = callback.data.split("p:rm:", 1)[1]
    if ":" in payload:
        payload = payload.split(":", 1)[0]
    participant_id = decode_uuid(payload)
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
        reply_markup=build_confirm_remove_keyboard(str(participant_id), None, None),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("p:cf:"))
async def participants_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    payload = callback.data.split("p:cf:", 1)[1]
    if ":" in payload:
        payload = payload.split(":", 1)[0]
    participant_id = decode_uuid(payload)
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
            participant_id,
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer("✅ Участник удалён.")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "participants:close")
async def participants_close(callback: CallbackQuery) -> None:
    from bot.keyboards.main_menu import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "participants:cancel")
async def participants_cancel(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return
