import uuid

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.common import CANCEL_CALLBACK, build_cancel_reply_keyboard, build_confirm_inline_keyboard
from bot.keyboards.onboarding import (
    CREATE_BUDGET_CALLBACK,
    JOIN_BUDGET_CALLBACK,
    SKIP_AUX_CURRENCY,
    USE_DEFAULT_TIMEZONE,
    build_default_timezone_keyboard,
    build_skip_aux_keyboard,
)
from bot.states.onboarding import CreateBudgetStates
from core.settings_app import app_settings
from services.budget_service import BudgetServiceError, create_first_budget
from services.dto.budget import CreateBudgetDTO
from services.start_service import build_join_budget_placeholder
from services.user_service import ensure_user

router = Router()


@router.callback_query(F.data == CREATE_BUDGET_CALLBACK)
async def create_budget_callback(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if callback.from_user is None:
        await callback.answer()
        return

    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    await state.update_data(owner_user_id=str(user.id))
    await state.set_state(CreateBudgetStates.name)

    await callback.message.answer(
        "Как назовём бюджет?",
        reply_markup=build_cancel_reply_keyboard(),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == JOIN_BUDGET_CALLBACK)
async def join_budget_callback(callback: CallbackQuery) -> None:
    await callback.message.answer(build_join_budget_placeholder())
    await _safe_callback_answer(callback)


@router.message(F.text.casefold() == "отмена")
async def cancel_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())


@router.callback_query(F.data == CANCEL_CALLBACK)
async def cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    await _safe_callback_answer(callback)


@router.message(CreateBudgetStates.name)
async def budget_name_step(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не должно быть пустым. Попробуй ещё раз.")
        return
    await state.update_data(name=name)
    await state.set_state(CreateBudgetStates.base_currency)
    await message.answer("Базовая валюта (3 буквы, например RUB):", reply_markup=build_cancel_reply_keyboard())


@router.message(CreateBudgetStates.base_currency)
async def budget_base_currency_step(message: Message, state: FSMContext) -> None:
    base_currency = (message.text or "").strip().upper()
    if len(base_currency) != 3:
        await message.answer("Нужно 3 буквы кода валюты (например, EUR).")
        return
    await state.update_data(base_currency=base_currency)
    await state.set_state(CreateBudgetStates.aux_currency_1)
    await message.answer(
        "Первая вспомогательная валюта (или пропусти):",
        reply_markup=build_skip_aux_keyboard(),
    )


@router.callback_query(F.data == SKIP_AUX_CURRENCY, CreateBudgetStates.aux_currency_1)
async def skip_aux_currency_1(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(aux_currency_1=None)
    await state.set_state(CreateBudgetStates.aux_currency_2)
    await callback.message.answer(
        "Вторая вспомогательная валюта (или пропусти):",
        reply_markup=build_skip_aux_keyboard(),
    )
    await _safe_callback_answer(callback)


@router.message(CreateBudgetStates.aux_currency_1)
async def budget_aux_currency_1_step(message: Message, state: FSMContext) -> None:
    if (message.text or "").strip().casefold() == "пропустить":
        await state.update_data(aux_currency_1=None)
        await state.set_state(CreateBudgetStates.aux_currency_2)
        await message.answer(
            "Вторая вспомогательная валюта (или пропусти):",
            reply_markup=build_skip_aux_keyboard(),
        )
        return
    aux_currency = (message.text or "").strip().upper()
    if len(aux_currency) != 3:
        await message.answer("Нужно 3 буквы кода валюты или нажми «Пропустить».")
        return
    await state.update_data(aux_currency_1=aux_currency)
    await state.set_state(CreateBudgetStates.aux_currency_2)
    await message.answer(
        "Вторая вспомогательная валюта (или пропусти):",
        reply_markup=build_skip_aux_keyboard(),
    )


@router.callback_query(F.data == SKIP_AUX_CURRENCY, CreateBudgetStates.aux_currency_2)
async def skip_aux_currency_2(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(aux_currency_2=None)
    await state.set_state(CreateBudgetStates.timezone)
    await callback.message.answer(
        "Таймзона бюджета (IANA, например Europe/Belgrade):",
        reply_markup=build_default_timezone_keyboard(app_settings.default_timezone),
    )
    await _safe_callback_answer(callback)


@router.message(CreateBudgetStates.aux_currency_2)
async def budget_aux_currency_2_step(message: Message, state: FSMContext) -> None:
    if (message.text or "").strip().casefold() == "пропустить":
        await state.update_data(aux_currency_2=None)
        await state.set_state(CreateBudgetStates.timezone)
        await message.answer(
            "Таймзона бюджета (IANA, например Europe/Belgrade):",
            reply_markup=build_default_timezone_keyboard(app_settings.default_timezone),
        )
        return
    aux_currency = (message.text or "").strip().upper()
    if len(aux_currency) != 3:
        await message.answer("Нужно 3 буквы кода валюты или нажми «Пропустить».")
        return
    await state.update_data(aux_currency_2=aux_currency)
    await state.set_state(CreateBudgetStates.timezone)
    await message.answer(
        "Таймзона бюджета (IANA, например Europe/Belgrade):",
        reply_markup=build_default_timezone_keyboard(app_settings.default_timezone),
    )


@router.callback_query(F.data == USE_DEFAULT_TIMEZONE, CreateBudgetStates.timezone)
async def use_default_timezone(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(timezone=app_settings.default_timezone)
    await _send_budget_summary(callback.message, state)
    await _safe_callback_answer(callback)


@router.message(CreateBudgetStates.timezone)
async def budget_timezone_step(message: Message, state: FSMContext) -> None:
    timezone = (message.text or "").strip()
    if not timezone:
        await message.answer("Таймзона не должна быть пустой.")
        return
    await state.update_data(timezone=timezone)
    await _send_budget_summary(message, state)


async def _send_budget_summary(target: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(CreateBudgetStates.confirm)
    text = (
        "Проверь данные 👇\n\n"
        f"Бюджет: {data.get('name')}\n"
        f"Базовая валюта: {data.get('base_currency')}\n"
        f"Вспомогательная 1: {data.get('aux_currency_1') or '—'}\n"
        f"Вспомогательная 2: {data.get('aux_currency_2') or '—'}\n"
        f"Таймзона: {data.get('timezone')}\n\n"
        "Создать бюджет?"
    )
    await target.answer(text, reply_markup=build_confirm_inline_keyboard())


@router.callback_query(F.data == "onboarding:confirm_budget", CreateBudgetStates.confirm)
async def confirm_budget(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    owner_user_id = data.get("owner_user_id")
    if owner_user_id is None:
        await callback.message.answer("Не нашёл пользователя. Попробуй /start ещё раз.")
        await state.clear()
        await _safe_callback_answer(callback)
        return

    owner_uuid = uuid.UUID(owner_user_id)

    try:
        payload = CreateBudgetDTO(
            name=data.get("name", ""),
            base_currency=data.get("base_currency", ""),
            aux_currency_1=data.get("aux_currency_1"),
            aux_currency_2=data.get("aux_currency_2"),
            timezone=data.get("timezone", app_settings.default_timezone),
        )
        await create_first_budget(session=session, owner_user_id=owner_uuid, payload=payload)
    except BudgetServiceError as exc:
        await callback.message.answer(f"Не удалось создать бюджет: {exc}")
        await state.set_state(CreateBudgetStates.base_currency)
        await _safe_callback_answer(callback)
        return
    except Exception:
        await callback.message.answer("Что-то пошло не так. Попробуй ещё раз.")
        await state.clear()
        await _safe_callback_answer(callback)
        return

    await state.clear()
    await callback.message.answer("✅ Бюджет создан.", reply_markup=ReplyKeyboardRemove())
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return
