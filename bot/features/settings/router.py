from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.main_menu.texts import build_section_text
from bot.features.settings.keyboards import (
    SETTINGS_BUDGETS,
    SETTINGS_BUDGETS_ACTIVE,
    SETTINGS_BUDGETS_INVITE,
    SETTINGS_BUDGETS_LIST,
    SETTINGS_BUDGETS_PARTICIPANTS,
    SETTINGS_CANCEL,
    SETTINGS_CATEGORIES,
    SETTINGS_CATEGORIES_EXPENSE,
    SETTINGS_CATEGORIES_INCOME,
    SETTINGS_CURRENCIES,
    SETTINGS_CURRENCY_AUX_1,
    SETTINGS_CURRENCY_AUX_2,
    SETTINGS_CURRENCY_BASE,
    SETTINGS_ROOT,
    build_settings_budgets_keyboard,
    build_settings_categories_keyboard,
    build_settings_currencies_keyboard,
    build_settings_root_keyboard,
)
from services.user_service import ensure_user

router = Router()


@router.message(F.text.startswith("/settings"))
async def settings_command(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    await ensure_user(
        session=session,
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    text = build_section_text("⚙️ НАСТРОЙКИ", "Выберите раздел")
    await message.answer(text, reply_markup=build_settings_root_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == SETTINGS_ROOT)
async def settings_root(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ НАСТРОЙКИ", "Выберите раздел")
    await _edit_or_answer(callback, text, reply_markup=build_settings_root_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == SETTINGS_BUDGETS)
async def settings_budgets(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ БЮДЖЕТЫ", "Выберите действие")
    await _edit_or_answer(callback, text, reply_markup=build_settings_budgets_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == SETTINGS_CURRENCIES)
async def settings_currencies(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ ВАЛЮТЫ", "Выберите раздел")
    await _edit_or_answer(callback, text, reply_markup=build_settings_currencies_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == SETTINGS_CATEGORIES)
async def settings_categories(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ КАТЕГОРИИ", "Выберите раздел")
    await _edit_or_answer(callback, text, reply_markup=build_settings_categories_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(
    F.data.in_(
        {
            SETTINGS_BUDGETS_LIST,
            SETTINGS_BUDGETS_ACTIVE,
            SETTINGS_BUDGETS_PARTICIPANTS,
            SETTINGS_BUDGETS_INVITE,
        }
    )
)
async def settings_budgets_placeholder(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ БЮДЖЕТЫ", "Сценарий будет добавлен позже.")
    await _edit_or_answer(callback, text, reply_markup=build_settings_budgets_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(
    F.data.in_(
        {
            SETTINGS_CURRENCY_BASE,
            SETTINGS_CURRENCY_AUX_1,
            SETTINGS_CURRENCY_AUX_2,
        }
    )
)
async def settings_currencies_placeholder(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ ВАЛЮТЫ", "Сценарий будет добавлен позже.")
    await _edit_or_answer(callback, text, reply_markup=build_settings_currencies_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(
    F.data.in_(
        {
            SETTINGS_CATEGORIES_EXPENSE,
            SETTINGS_CATEGORIES_INCOME,
        }
    )
)
async def settings_categories_placeholder(callback: CallbackQuery) -> None:
    text = build_section_text("⚙️ КАТЕГОРИИ", "Сценарий будет добавлен позже.")
    await _edit_or_answer(callback, text, reply_markup=build_settings_categories_keyboard(), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == SETTINGS_CANCEL)
async def settings_cancel(callback: CallbackQuery) -> None:
    await settings_root(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return None


async def _edit_or_answer(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    parse_mode: str | None = None,
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
