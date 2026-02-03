from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.main_menu.home import render_root_for_callback, render_root_for_message
from bot.features.main_menu.keyboards import (
    BACK_TO_EXPENSE_AMOUNT,
    BACK_TO_EXPENSE_CURRENCY,
    BACK_TO_HOME,
    BACK_TO_INCOME_AMOUNT,
    BACK_TO_INCOME_CURRENCY,
    EXPENSE_CATEGORY_PREFIX,
    EXPENSE_CONFIRM,
    EXPENSE_CURRENCY_PREFIX,
    EXPENSE_DONE,
    EXPENSE_EDIT,
    EXPENSE_MORE,
    EXPENSE_REPEAT,
    GOALS_ADD,
    GOALS_CREATE,
    GOALS_LIST,
    GOALS_ROOT,
    GOALS_WITHDRAW,
    INCOME_CONFIRM,
    INCOME_CURRENCY_PREFIX,
    INCOME_DONE,
    INCOME_EDIT,
    INCOME_MORE,
    INCOME_REPEAT,
    INCOME_SOURCE_PREFIX,
    REPORTS_GOALS,
    REPORTS_OPERATIONS,
    REPORTS_ROOT,
    REPORTS_SUMMARY,
    EXPENSE_CATEGORIES,
    INCOME_SOURCES,
    build_back_keyboard,
    build_confirm_keyboard,
    build_done_keyboard,
    build_expense_categories_keyboard,
    build_expense_currency_keyboard,
    build_goals_root_keyboard,
    build_income_currency_keyboard,
    build_income_sources_keyboard,
    build_reports_root_keyboard,
)
from bot.features.main_menu.states import ExpenseStates, IncomeStates
from bot.features.main_menu.texts import build_breadcrumbs, build_section_text
from bot.features.onboarding.keyboards import BASE_CURRENCIES
from db.models.budget import Budget
from services.active_budget_service import get_active_budget_id
from services.user_service import ensure_user

router = Router()


@router.message(F.text.startswith("/main_menu") | F.text.startswith("/main-menu"))
async def main_menu_command(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    user = await ensure_user(
        session=session,
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await render_root_for_message(message, session, str(user.id))


@router.callback_query(F.data == "main:income")
async def menu_income(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IncomeStates.amount)
    await state.update_data(flow_message_id=callback.message.message_id)
    text = build_section_text("💰 ПРИХОД", "Введите сумму")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(BACK_TO_HOME), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "main:expense")
async def menu_expense(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ExpenseStates.amount)
    await state.update_data(flow_message_id=callback.message.message_id)
    text = build_section_text("💸 РАСХОД", "Введите сумму")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(BACK_TO_HOME), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "main:goals")
async def menu_goals(callback: CallbackQuery) -> None:
    await _render_goals_root(callback)


@router.callback_query(F.data == "main:reports")
async def menu_reports(callback: CallbackQuery) -> None:
    await _render_reports_root(callback)


@router.callback_query(F.data == GOALS_ROOT)
async def goals_root(callback: CallbackQuery) -> None:
    await _render_goals_root(callback)


@router.callback_query(F.data == REPORTS_ROOT)
async def reports_root(callback: CallbackQuery) -> None:
    await _render_reports_root(callback)


@router.callback_query(F.data == GOALS_CREATE)
async def goals_create(callback: CallbackQuery) -> None:
    text = build_section_text("🎯 ЦЕЛИ", "Сценарий создания цели скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(GOALS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == GOALS_ADD)
async def goals_add(callback: CallbackQuery) -> None:
    text = build_section_text("🎯 ЦЕЛИ", "Сценарий пополнения скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(GOALS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == GOALS_WITHDRAW)
async def goals_withdraw(callback: CallbackQuery) -> None:
    text = build_section_text("🎯 ЦЕЛИ", "Сценарий снятия скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(GOALS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == GOALS_LIST)
async def goals_list(callback: CallbackQuery) -> None:
    text = build_section_text("🎯 ЦЕЛИ", "Список целей скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(GOALS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == REPORTS_SUMMARY)
async def reports_summary(callback: CallbackQuery) -> None:
    text = build_section_text("📊 ОТЧЕТЫ", "Сценарий сводки скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(REPORTS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == REPORTS_OPERATIONS)
async def reports_operations(callback: CallbackQuery) -> None:
    text = build_section_text("📊 ОТЧЕТЫ", "Сценарий операций скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(REPORTS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == REPORTS_GOALS)
async def reports_goals(callback: CallbackQuery) -> None:
    text = build_section_text("📊 ОТЧЕТЫ", "Сценарий целей скоро появится.")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(REPORTS_ROOT), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == BACK_TO_HOME)
async def nav_back_home(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()
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
    await render_root_for_callback(callback, session, str(user.id))


@router.callback_query(F.data == BACK_TO_EXPENSE_AMOUNT)
async def nav_back_expense_amount(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ExpenseStates.amount)
    text = build_section_text("💸 РАСХОД", "Введите сумму")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(BACK_TO_HOME), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == BACK_TO_EXPENSE_CURRENCY)
async def nav_back_expense_currency(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.set_state(ExpenseStates.currency)
    currencies = await _get_budget_currencies(callback.from_user, session)
    breadcrumb = build_breadcrumbs("расход", "ВАЛЮТА")
    text = f"{breadcrumb}\nВыберите валюту"
    await callback.message.edit_text(
        text,
        reply_markup=build_expense_currency_keyboard(currencies),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == BACK_TO_INCOME_AMOUNT)
async def nav_back_income_amount(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IncomeStates.amount)
    text = build_section_text("💰 ПРИХОД", "Введите сумму")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(BACK_TO_HOME), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == BACK_TO_INCOME_CURRENCY)
async def nav_back_income_currency(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.set_state(IncomeStates.currency)
    currencies = await _get_budget_currencies(callback.from_user, session)
    breadcrumb = build_breadcrumbs("приход", "ВАЛЮТА")
    text = f"{breadcrumb}\nВыберите валюту"
    await callback.message.edit_text(
        text,
        reply_markup=build_income_currency_keyboard(currencies),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


@router.message(ExpenseStates.amount)
async def expense_amount_step(message: Message, state: FSMContext, session: AsyncSession) -> None:
    text_raw = (message.text or "").strip()
    if not text_raw:
        await message.answer("Не понял сумму. Попробуй ещё раз.")
        return
    await state.update_data(expense_amount=text_raw)
    await state.set_state(ExpenseStates.currency)
    currencies = await _get_budget_currencies(message.from_user, session)
    breadcrumb = build_breadcrumbs("расход", "ВАЛЮТА")
    text = f"{breadcrumb}\nВыберите валюту"
    data = await state.get_data()
    msg_id = data.get("flow_message_id")
    await _edit_flow_message(
        message,
        msg_id,
        text,
        reply_markup=build_expense_currency_keyboard(currencies),
        parse_mode="HTML",
    )


@router.message(IncomeStates.amount)
async def income_amount_step(message: Message, state: FSMContext, session: AsyncSession) -> None:
    text_raw = (message.text or "").strip()
    if not text_raw:
        await message.answer("Не понял сумму. Попробуй ещё раз.")
        return
    await state.update_data(income_amount=text_raw)
    await state.set_state(IncomeStates.currency)
    currencies = await _get_budget_currencies(message.from_user, session)
    breadcrumb = build_breadcrumbs("приход", "ВАЛЮТА")
    text = f"{breadcrumb}\nВыберите валюту"
    data = await state.get_data()
    msg_id = data.get("flow_message_id")
    await _edit_flow_message(
        message,
        msg_id,
        text,
        reply_markup=build_income_currency_keyboard(currencies),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith(EXPENSE_CURRENCY_PREFIX), ExpenseStates.currency)
async def expense_currency_pick(callback: CallbackQuery, state: FSMContext) -> None:
    currency = callback.data.split(EXPENSE_CURRENCY_PREFIX, 1)[1]
    await state.update_data(expense_currency=currency)
    await state.set_state(ExpenseStates.category)
    breadcrumb = build_breadcrumbs("расход", "КАТЕГОРИЯ")
    if not EXPENSE_CATEGORIES:
        text = f"{breadcrumb}\nКатегории еще не настроены"
        await callback.message.edit_text(
            text,
            reply_markup=build_back_keyboard(BACK_TO_EXPENSE_CURRENCY),
            parse_mode="HTML",
        )
        await _safe_callback_answer(callback)
        return
    text = f"{breadcrumb}\nВыберите категорию"
    await callback.message.edit_text(
        text,
        reply_markup=build_expense_categories_keyboard(),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith(INCOME_CURRENCY_PREFIX), IncomeStates.currency)
async def income_currency_pick(callback: CallbackQuery, state: FSMContext) -> None:
    currency = callback.data.split(INCOME_CURRENCY_PREFIX, 1)[1]
    await state.update_data(income_currency=currency)
    await state.set_state(IncomeStates.source)
    breadcrumb = build_breadcrumbs("приход", "ИСТОЧНИК")
    if not INCOME_SOURCES:
        text = f"{breadcrumb}\nИсточники еще не настроены"
        await callback.message.edit_text(
            text,
            reply_markup=build_back_keyboard(BACK_TO_INCOME_CURRENCY),
            parse_mode="HTML",
        )
        await _safe_callback_answer(callback)
        return
    text = f"{breadcrumb}\nВыберите источник"
    await callback.message.edit_text(
        text,
        reply_markup=build_income_sources_keyboard(),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith(EXPENSE_CATEGORY_PREFIX), ExpenseStates.category)
async def expense_category_pick(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(EXPENSE_CATEGORY_PREFIX, 1)[1]
    label = _find_label(EXPENSE_CATEGORIES, key)
    await state.update_data(expense_category=label)
    await state.set_state(ExpenseStates.confirm)
    data = await state.get_data()
    text = _build_expense_confirm_text(data)
    await callback.message.edit_text(
        text,
        reply_markup=build_confirm_keyboard(EXPENSE_CONFIRM, EXPENSE_EDIT),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith(INCOME_SOURCE_PREFIX), IncomeStates.source)
async def income_source_pick(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(INCOME_SOURCE_PREFIX, 1)[1]
    label = _find_label(INCOME_SOURCES, key)
    await state.update_data(income_source=label)
    await state.set_state(IncomeStates.confirm)
    data = await state.get_data()
    text = _build_income_confirm_text(data)
    await callback.message.edit_text(
        text,
        reply_markup=build_confirm_keyboard(INCOME_CONFIRM, INCOME_EDIT),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == EXPENSE_EDIT)
async def expense_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ExpenseStates.category)
    breadcrumb = build_breadcrumbs("расход", "КАТЕГОРИЯ")
    if not EXPENSE_CATEGORIES:
        text = f"{breadcrumb}\nКатегории еще не настроены"
        await callback.message.edit_text(
            text,
            reply_markup=build_back_keyboard(BACK_TO_EXPENSE_CURRENCY),
            parse_mode="HTML",
        )
        await _safe_callback_answer(callback)
        return
    text = f"{breadcrumb}\nВыберите категорию"
    await callback.message.edit_text(
        text,
        reply_markup=build_expense_categories_keyboard(),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == INCOME_EDIT)
async def income_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IncomeStates.source)
    breadcrumb = build_breadcrumbs("приход", "ИСТОЧНИК")
    if not INCOME_SOURCES:
        text = f"{breadcrumb}\nИсточники еще не настроены"
        await callback.message.edit_text(
            text,
            reply_markup=build_back_keyboard(BACK_TO_INCOME_CURRENCY),
            parse_mode="HTML",
        )
        await _safe_callback_answer(callback)
        return
    text = f"{breadcrumb}\nВыберите источник"
    await callback.message.edit_text(
        text,
        reply_markup=build_income_sources_keyboard(),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == EXPENSE_CONFIRM, ExpenseStates.confirm)
async def expense_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = _build_expense_done_text(data)
    await callback.message.edit_text(
        text,
        reply_markup=build_done_keyboard("Еще расход", EXPENSE_MORE, EXPENSE_REPEAT, EXPENSE_DONE),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == INCOME_CONFIRM, IncomeStates.confirm)
async def income_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = _build_income_done_text(data)
    await callback.message.edit_text(
        text,
        reply_markup=build_done_keyboard("Еще приход", INCOME_MORE, INCOME_REPEAT, INCOME_DONE),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == EXPENSE_MORE)
async def expense_more(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ExpenseStates.amount)
    await state.update_data(expense_amount=None, expense_currency=None, expense_category=None)
    text = build_section_text("💸 РАСХОД", "Введите сумму")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(BACK_TO_HOME), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == INCOME_MORE)
async def income_more(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IncomeStates.amount)
    await state.update_data(income_amount=None, income_currency=None, income_source=None)
    text = build_section_text("💰 ПРИХОД", "Введите сумму")
    await callback.message.edit_text(text, reply_markup=build_back_keyboard(BACK_TO_HOME), parse_mode="HTML")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == EXPENSE_REPEAT)
async def expense_repeat(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ExpenseStates.confirm)
    data = await state.get_data()
    text = _build_expense_confirm_text(data)
    await callback.message.edit_text(
        text,
        reply_markup=build_confirm_keyboard(EXPENSE_CONFIRM, EXPENSE_EDIT),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == INCOME_REPEAT)
async def income_repeat(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IncomeStates.confirm)
    data = await state.get_data()
    text = _build_income_confirm_text(data)
    await callback.message.edit_text(
        text,
        reply_markup=build_confirm_keyboard(INCOME_CONFIRM, INCOME_EDIT),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == EXPENSE_DONE)
async def expense_done(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
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
    await render_root_for_callback(callback, session, str(user.id))


@router.callback_query(F.data == INCOME_DONE)
async def income_done(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
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
    await render_root_for_callback(callback, session, str(user.id))


async def _render_goals_root(callback: CallbackQuery) -> None:
    text = build_section_text("🎯 ЦЕЛИ", "Выберите действие")
    await callback.message.edit_text(
        text,
        reply_markup=build_goals_root_keyboard(),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


async def _render_reports_root(callback: CallbackQuery) -> None:
    text = build_section_text("📊 ОТЧЕТЫ", "Выберите раздел")
    await callback.message.edit_text(
        text,
        reply_markup=build_reports_root_keyboard(),
        parse_mode="HTML",
    )
    await _safe_callback_answer(callback)


async def _get_budget_currencies(user, session: AsyncSession) -> list[str]:
    if user is None:
        return list(BASE_CURRENCIES)
    user_row = await ensure_user(
        session=session,
        telegram_user_id=user.id,
        telegram_username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    active_budget_id = await get_active_budget_id(session, user_row.id)
    if active_budget_id is None:
        return list(BASE_CURRENCIES)
    budget = await session.get(Budget, active_budget_id)
    if budget is None:
        return list(BASE_CURRENCIES)
    currencies = [budget.base_currency, budget.aux_currency_1, budget.aux_currency_2]
    return [currency for currency in currencies if currency]


def _find_label(items: list[tuple[str, str]], key: str) -> str:
    for item_key, label in items:
        if item_key == key:
            return label
    return key


def _build_expense_confirm_text(data: dict) -> str:
    amount = data.get("expense_amount", "—")
    currency = data.get("expense_currency", "—")
    category = data.get("expense_category", "—")
    return (
        "Проверьте\n\n"
        f"💸 -{amount} {currency}\n"
        f"Категория: {category}"
    )


def _build_income_confirm_text(data: dict) -> str:
    amount = data.get("income_amount", "—")
    currency = data.get("income_currency", "—")
    source = data.get("income_source", "—")
    return (
        "Проверьте\n\n"
        f"💰 +{amount} {currency}\n"
        f"Источник: {source}"
    )


def _build_expense_done_text(data: dict) -> str:
    amount = data.get("expense_amount", "—")
    currency = data.get("expense_currency", "—")
    category = data.get("expense_category", "—")
    return (
        "✅ Расход сохранен\n\n"
        f"💸 -{amount} {currency}\n"
        f"Категория: {category}\n"
        "№—"
    )


def _build_income_done_text(data: dict) -> str:
    amount = data.get("income_amount", "—")
    currency = data.get("income_currency", "—")
    source = data.get("income_source", "—")
    return (
        "✅ Приход сохранен\n\n"
        f"💰 +{amount} {currency}\n"
        f"Источник: {source}\n"
        "№—"
    )


async def _edit_flow_message(
    message: Message,
    msg_id: int | None,
    text: str,
    reply_markup=None,
    parse_mode: str | None = None,
) -> None:
    if msg_id is None:
        await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
        return
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except TelegramBadRequest:
        await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return
