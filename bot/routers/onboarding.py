from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.onboarding import CREATE_BUDGET_CALLBACK, JOIN_BUDGET_CALLBACK
from services.start_service import build_create_budget_placeholder, build_join_budget_placeholder

router = Router()


@router.callback_query(F.data == CREATE_BUDGET_CALLBACK)
async def create_budget_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(build_create_budget_placeholder())
    await callback.answer()


@router.callback_query(F.data == JOIN_BUDGET_CALLBACK)
async def join_budget_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(build_join_budget_placeholder())
    await callback.answer()
