import logging
import uuid

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.main_menu.keyboards import build_main_menu_keyboard
from bot.features.budgets.keyboards import build_budgets_menu_keyboard
from bot.features.onboarding.keyboards import (
    CANCEL_CALLBACK,
    CREATE_BUDGET_CALLBACK,
    INVITE_BUDGET_CALLBACK,
    JOIN_BUDGET_CALLBACK,
    build_confirm_inline_keyboard,
    build_home_reply_keyboard,
    build_invite_confirm_keyboard,
    HOME_REPLY_TEXT,
)
from bot.features.onboarding.states import CreateBudgetStates, JoinBudgetStates
from core.settings_app import app_settings
from services.budget_service import BudgetServiceError, create_first_budget
from services.dto.budget import CreateBudgetDTO
from services.invite_service import (
    InviteServiceError,
    accept_invite,
    create_invite_for_owner,
    get_invite_preview,
)
from services.start_service import build_start_message
from services.user_service import ensure_user

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if message.from_user is not None:
        user = await ensure_user(
            session=session,
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

        token = _extract_start_invite_token(message.text or "")
        if token is not None:
            try:
                invite, budget_name, owner_username = await get_invite_preview(session, token)
                await state.update_data(invite_token=invite.token, invite_user_id=str(user.id))
                await state.set_state(JoinBudgetStates.confirm)
                owner_text = f"@{owner_username}" if owner_username else "пользователь"
                await message.answer(
                    f'{owner_text} пригласил вас в совместный бюджет "{budget_name}".',
                    reply_markup=build_invite_confirm_keyboard(),
                )
            except InviteServiceError as exc:
                await message.answer(f"Не удалось присоединиться: {exc}")
            return

    response_text = build_start_message()
    await message.answer(response_text)
    await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())


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
        reply_markup=build_home_reply_keyboard(),
    )
    await _safe_callback_answer(callback)


@router.message(F.text.casefold() == "создать бюджет")
async def create_budget_message(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    user = await ensure_user(
        session=session,
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await state.update_data(owner_user_id=str(user.id))
    await state.set_state(CreateBudgetStates.name)
    await message.answer("Как назовём бюджет?", reply_markup=build_home_reply_keyboard())


@router.callback_query(F.data == JOIN_BUDGET_CALLBACK)
async def join_budget_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(JoinBudgetStates.token)
    await callback.message.answer(
        "Пришли инвайт-ссылку или код приглашения.",
        reply_markup=build_home_reply_keyboard(),
    )
    await _safe_callback_answer(callback)


@router.message(F.text.casefold() == "присоединиться")
async def join_budget_message(message: Message, state: FSMContext) -> None:
    await state.set_state(JoinBudgetStates.token)
    await message.answer(
        "Пришли инвайт-ссылку или код приглашения.",
        reply_markup=build_home_reply_keyboard(),
    )


@router.callback_query(F.data == INVITE_BUDGET_CALLBACK)
async def invite_budget_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
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
        invite = await create_invite_for_owner(session, user.id)
        bot_username = (await callback.bot.get_me()).username
        if not bot_username:
            await callback.message.answer("Не удалось получить имя бота. Попробуй позже.")
            await _safe_callback_answer(callback)
            return
        link = f"https://t.me/{bot_username}?start=invite_{invite.token}"
        await callback.message.answer(
            "Готово 👇\n\n"
            f"Ссылка действует 24 часа и используется один раз:\n{link}"
        )
    except InviteServiceError as exc:
        await callback.message.answer(f"Не удалось создать приглашение: {exc}")
    await _safe_callback_answer(callback)


@router.message(F.text.casefold() == "отмена")
async def cancel_message(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await state.clear()
    if current_state in {
        JoinBudgetStates.token.state,
        JoinBudgetStates.confirm.state,
        CreateBudgetStates.name.state,
        CreateBudgetStates.base_currency.state,
        CreateBudgetStates.aux_currency_1.state,
        CreateBudgetStates.aux_currency_2.state,
        CreateBudgetStates.timezone.state,
        CreateBudgetStates.confirm.state,
    }:
        await message.answer(build_start_message())
        await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    else:
        await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == HOME_REPLY_TEXT)
async def home_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(build_start_message())
    await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())


@router.callback_query(F.data == CANCEL_CALLBACK)
async def cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    await state.clear()
    if current_state in {
        JoinBudgetStates.token.state,
        JoinBudgetStates.confirm.state,
        CreateBudgetStates.name.state,
        CreateBudgetStates.base_currency.state,
        CreateBudgetStates.aux_currency_1.state,
        CreateBudgetStates.aux_currency_2.state,
        CreateBudgetStates.timezone.state,
        CreateBudgetStates.confirm.state,
    }:
        await callback.message.answer(build_start_message())
        await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    else:
        await callback.message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    await _safe_callback_answer(callback)


@router.message(CreateBudgetStates.name)
async def budget_name_step(message: Message, state: FSMContext) -> None:
    if (message.text or "").strip().casefold() in {"назад", HOME_REPLY_TEXT.casefold()}:
        await state.clear()
        await message.answer(build_start_message())
        await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
        return
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не должно быть пустым. Попробуй ещё раз.")
        return
    await state.update_data(name=name)
    await state.set_state(CreateBudgetStates.base_currency)
    await message.answer(
        "Базовая валюта (3 буквы, например RUB):",
        reply_markup=build_home_reply_keyboard(),
    )


@router.message(JoinBudgetStates.token)
async def join_budget_token_step(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.from_user is None:
        await message.answer("Не нашёл пользователя. Попробуй /start ещё раз.")
        await state.clear()
        return
    text_raw = message.text or ""
    text = text_raw.strip()
    if text.casefold() in {"отмена", "назад", HOME_REPLY_TEXT.casefold()} or text.startswith("/start"):
        await state.clear()
        await message.answer(build_start_message())
        await message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
        return
    if text.casefold() == "бюджеты":
        await state.clear()
        await message.answer("Меню бюджетов:", reply_markup=build_budgets_menu_keyboard())
        return
    token = _extract_invite_token(text_raw)
    if token is None:
        await message.answer("Не вижу токен. Пришли ссылку или код вида invite_XXXX.")
        return
    user = await ensure_user(
        session=session,
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    try:
        invite, budget_name, owner_username = await get_invite_preview(session, token)
    except InviteServiceError as exc:
        await message.answer(f"Не удалось присоединиться: {exc}")
        await state.clear()
        return

    await state.update_data(invite_token=invite.token, invite_user_id=str(user.id))
    await state.set_state(JoinBudgetStates.confirm)
    owner_text = f"@{owner_username}" if owner_username else "пользователь"
    await message.answer(
        f'{owner_text} пригласил вас в совместный бюджет "{budget_name}".',
        reply_markup=build_invite_confirm_keyboard(),
    )


@router.callback_query(F.data == "onboarding:accept_invite", JoinBudgetStates.confirm)
async def accept_invite_callback(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    token = data.get("invite_token")
    user_id = data.get("invite_user_id")
    if token is None or user_id is None:
        await callback.message.answer("Не найден инвайт. Попробуй ещё раз.")
        await state.clear()
        await _safe_callback_answer(callback)
        return
    try:
        await accept_invite(session, token, uuid.UUID(user_id))
    except InviteServiceError as exc:
        await callback.message.answer(f"Не удалось присоединиться: {exc}")
        await state.clear()
        await _safe_callback_answer(callback)
        return
    await state.clear()
    await callback.message.answer("✅ Ты присоединился к бюджету.", reply_markup=ReplyKeyboardRemove())
    await _safe_callback_answer(callback)


@router.message(CreateBudgetStates.base_currency)
async def budget_base_currency_step(message: Message, state: FSMContext) -> None:
    if (message.text or "").strip().casefold() in {"назад", HOME_REPLY_TEXT.casefold()}:
        await state.set_state(CreateBudgetStates.name)
        await state.update_data(base_currency=None, aux_currency_1=None, aux_currency_2=None, timezone=None)
        await message.answer("Как назовём бюджет?", reply_markup=build_home_reply_keyboard())
        return
    base_currency = (message.text or "").strip().upper()
    if len(base_currency) != 3:
        await message.answer("Нужно 3 буквы кода валюты (например, EUR).")
        return
    await state.update_data(base_currency=base_currency)
    await state.set_state(CreateBudgetStates.aux_currency_1)
    await message.answer(
        "Первая вспомогательная валюта (или пропусти):",
        reply_markup=build_home_reply_keyboard(),
    )


@router.message(CreateBudgetStates.aux_currency_1)
async def budget_aux_currency_1_step(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if text.casefold() in {"назад", HOME_REPLY_TEXT.casefold()}:
        await state.set_state(CreateBudgetStates.base_currency)
        await state.update_data(aux_currency_1=None, aux_currency_2=None, timezone=None)
        await message.answer(
            "Базовая валюта (3 буквы, например RUB):",
            reply_markup=build_home_reply_keyboard(),
        )
        return
    if text.casefold() == "пропустить":
        await state.update_data(aux_currency_1=None)
        await state.set_state(CreateBudgetStates.aux_currency_2)
        await message.answer(
            "Вторая вспомогательная валюта (или пропусти):",
            reply_markup=build_home_reply_keyboard(),
        )
        return
    aux_currency = text.upper()
    if len(aux_currency) != 3:
        await message.answer("Нужно 3 буквы кода валюты или нажми «Пропустить».")
        return
    await state.update_data(aux_currency_1=aux_currency)
    await state.set_state(CreateBudgetStates.aux_currency_2)
    await message.answer(
        "Вторая вспомогательная валюта (или пропусти):",
        reply_markup=build_home_reply_keyboard(),
    )


@router.message(CreateBudgetStates.aux_currency_2)
async def budget_aux_currency_2_step(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if text.casefold() in {"назад", HOME_REPLY_TEXT.casefold()}:
        await state.set_state(CreateBudgetStates.aux_currency_1)
        await state.update_data(aux_currency_2=None, timezone=None)
        await message.answer(
            "Первая вспомогательная валюта (или пропусти):",
            reply_markup=build_home_reply_keyboard(),
        )
        return
    if text.casefold() == "пропустить":
        await state.update_data(aux_currency_2=None)
        await state.set_state(CreateBudgetStates.timezone)
        await message.answer(
            "Таймзона бюджета (IANA, например Europe/Belgrade):",
            reply_markup=build_home_reply_keyboard(),
        )
        return
    aux_currency = text.upper()
    if len(aux_currency) != 3:
        await message.answer("Нужно 3 буквы кода валюты или нажми «Пропустить».")
        return
    await state.update_data(aux_currency_2=aux_currency)
    await state.set_state(CreateBudgetStates.timezone)
    await message.answer(
        "Таймзона бюджета (IANA, например Europe/Belgrade):",
        reply_markup=build_home_reply_keyboard(),
    )


@router.message(CreateBudgetStates.timezone)
async def budget_timezone_step(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if text.casefold() in {"назад", HOME_REPLY_TEXT.casefold()}:
        await state.set_state(CreateBudgetStates.aux_currency_2)
        await message.answer(
            "Вторая вспомогательная валюта (или пропусти):",
            reply_markup=build_home_reply_keyboard(),
        )
        return
    if text == f"Оставить {app_settings.default_timezone}":
        await state.update_data(timezone=app_settings.default_timezone)
        await _send_budget_summary(message, state)
        return
    timezone = text
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
        logger.exception("Create budget failed", extra={"owner_user_id": owner_user_id, "data": data})
        await callback.message.answer("Что-то пошло не так. Попробуй ещё раз.")
        await state.clear()
        await _safe_callback_answer(callback)
        return

    await state.clear()
    await callback.message.answer("✅ Бюджет создан.", reply_markup=ReplyKeyboardRemove())
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "onboarding:edit_budget", CreateBudgetStates.confirm)
async def edit_budget(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateBudgetStates.timezone)
    await callback.message.answer(
        "Таймзона бюджета (IANA, например Europe/Belgrade):",
        reply_markup=build_home_reply_keyboard(),
    )
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return


def _extract_invite_token(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None
    if "start=invite_" in text:
        return text.split("start=invite_", 1)[1].strip()
    if text.startswith("invite_"):
        return text.replace("invite_", "", 1).strip()
    return None


def _extract_start_invite_token(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None
    if "start=invite_" in text:
        return text.split("start=invite_", 1)[1].strip()
    if text.startswith("/start "):
        payload = text.split(" ", 1)[1].strip()
        if payload.startswith("invite_"):
            return payload.replace("invite_", "", 1).strip()
    return None
