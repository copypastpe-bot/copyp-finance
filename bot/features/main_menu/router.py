from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.budgets.keyboards import build_active_budget_keyboard, build_budgets_menu_keyboard
from services.active_budget_service import get_active_budget_id, list_user_budgets
from services.user_service import ensure_user

router = Router()


@router.message(F.text.casefold() == "бюджеты")
async def menu_budgets(message: Message) -> None:
    await message.answer("Меню бюджетов:", reply_markup=build_budgets_menu_keyboard())


@router.message(F.text.casefold() == "добавить приход")
async def menu_income(message: Message) -> None:
    await message.answer("Сценарий прихода скоро появится.")


@router.message(F.text.casefold() == "добавить расход")
async def menu_expense(message: Message) -> None:
    await message.answer("Сценарий расхода скоро появится.")


@router.message(F.text.casefold() == "цели")
async def menu_goals(message: Message) -> None:
    await message.answer("Сценарий целей скоро появится.")


@router.message(F.text.casefold() == "отчёты")
async def menu_reports(message: Message) -> None:
    await message.answer("Сценарий отчётов скоро появится.")


@router.message(F.text.casefold() == "назад")
async def menu_back(message: Message) -> None:
    from bot.features.main_menu.keyboards import build_main_menu_keyboard

    await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())


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
