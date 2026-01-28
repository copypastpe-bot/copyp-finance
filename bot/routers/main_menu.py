from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.budgets import build_active_budget_keyboard
from services.active_budget_service import list_user_budgets
from services.user_service import ensure_user

router = Router()


@router.message(F.text.casefold() == "бюджеты")
async def menu_budgets(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    user = await ensure_user(
        session=session,
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    items = await list_user_budgets(session, user.id)
    if not items:
        await message.answer("Бюджетов нет.")
        return
    await message.answer(
        "Выбери активный бюджет:", reply_markup=build_active_budget_keyboard(items)
    )


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
