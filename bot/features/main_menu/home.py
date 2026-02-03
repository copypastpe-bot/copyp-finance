from typing import Optional

from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.main_menu.keyboards import build_main_menu_keyboard
from bot.features.main_menu.texts import build_first_run_text, build_home_text
from bot.features.onboarding.keyboards import build_first_run_keyboard
from services.active_budget_service import get_active_budget_id, list_user_budgets


async def _get_budget_name(session: AsyncSession, user_id: str) -> Optional[str]:
    items = await list_user_budgets(session, user_id)
    if not items:
        return None
    active_id = await get_active_budget_id(session, user_id)
    if active_id is not None:
        for item in items:
            if item.get("budget_id") == str(active_id):
                return item.get("name") or ""
    return items[0].get("name") or ""


async def render_root_for_message(message: Message, session: AsyncSession, user_id: str) -> None:
    name = await _get_budget_name(session, user_id)
    if not name:
        await message.answer(build_first_run_text(), reply_markup=build_first_run_keyboard(), parse_mode="HTML")
        return
    await message.answer(build_home_text(name), reply_markup=build_main_menu_keyboard(), parse_mode="HTML")


async def render_root_for_callback(callback: CallbackQuery, session: AsyncSession, user_id: str) -> None:
    name = await _get_budget_name(session, user_id)
    if not name:
        await callback.message.edit_text(
            build_first_run_text(),
            reply_markup=build_first_run_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        build_home_text(name),
        reply_markup=build_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
