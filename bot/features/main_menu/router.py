from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.budgets.keyboards import build_active_budget_keyboard, build_budgets_menu_keyboard
from bot.features.main_menu.keyboards import build_main_menu_keyboard
from services.start_service import build_start_message
from services.active_budget_service import get_active_budget_id, list_user_budgets
from services.user_service import ensure_user

router = Router()


@router.message(F.text.startswith("/main_menu"))
async def main_menu_command(message: Message) -> None:
    await message.answer(build_start_message())
    await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())


@router.callback_query(F.data == "main:budgets")
async def menu_budgets(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Меню бюджетов:",
        reply_markup=build_budgets_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "main:income")
async def menu_income(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Сценарий прихода скоро появится.")
    await callback.answer()


@router.callback_query(F.data == "main:expense")
async def menu_expense(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Сценарий расхода скоро появится.")
    await callback.answer()


@router.callback_query(F.data == "main:goals")
async def menu_goals(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Сценарий целей скоро появится.")
    await callback.answer()


@router.callback_query(F.data == "main:reports")
async def menu_reports(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Сценарий отчётов скоро появится.")
    await callback.answer()


@router.message(F.text.casefold() == "мои бюджеты")
async def menu_my_budgets(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    user = await ensure_user(
        session=session,
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    active_budget_id = await get_active_budget_id(session, user.id)
    items = await list_user_budgets(session, user.id)
    if not items:
        await message.answer("Бюджетов нет.")
        return
    for item in items:
        if active_budget_id is not None and item["budget_id"] == str(active_budget_id):
            item["name"] = f"⭐ {item['name']}"
    await message.answer("Мои бюджеты:", reply_markup=build_active_budget_keyboard(items))
