import uuid

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.budgets import build_active_budget_keyboard
from services.active_budget_service import (
    ActiveBudgetServiceError,
    list_user_budgets,
    set_active_budget,
)
from services.user_service import ensure_user

router = Router()


@router.callback_query(F.data == "budgets:active")
async def active_budget_list(callback: CallbackQuery, session: AsyncSession) -> None:
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
    items = await list_user_budgets(session, user.id)
    if not items:
        await callback.message.answer("Бюджетов нет.")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer(
        "Выбери активный бюджет:", reply_markup=build_active_budget_keyboard(items)
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("budgets:set:"))
async def active_budget_set(callback: CallbackQuery, session: AsyncSession) -> None:
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
    budget_id = callback.data.split("budgets:set:", 1)[1]
    try:
        budget = await set_active_budget(session, user.id, uuid.UUID(budget_id))
    except ActiveBudgetServiceError as exc:
        await callback.message.answer(f"Не удалось выбрать бюджет: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer(f"Активный бюджет: {budget.name}")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budgets:close")
async def budgets_close(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return
