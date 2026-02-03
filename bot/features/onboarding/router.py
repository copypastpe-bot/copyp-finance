import logging
import uuid

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.main_menu.home import render_root_for_callback, render_root_for_message
from bot.features.main_menu.texts import build_greeting_text, build_section_text
from bot.features.onboarding.keyboards import (
    CANCEL_CALLBACK,
    CREATE_BUDGET_CALLBACK,
    INVITE_BUDGET_CALLBACK,
    JOIN_BUDGET_CALLBACK,
    FIRST_RUN_BACK,
    AUX_CURRENCY_PREFIX,
    AUX_SKIP_CALLBACK,
    BASE_CURRENCY_PREFIX,
    BASE_CURRENCIES,
    TIMEZONE_PREFIX,
    build_confirm_inline_keyboard,
    build_base_currency_keyboard,
    build_aux_currency_keyboard,
    build_first_run_back_keyboard,
    build_home_reply_keyboard,
    build_invite_confirm_keyboard,
    build_timezone_keyboard,
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
from services.user_service import ensure_user

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession, state: FSMContext) -> None:
    user = None
    first_name = message.from_user.first_name if message.from_user else None
    if message.from_user is not None:
        user = await ensure_user(
            session=session,
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

    greeting = build_greeting_text(first_name)
    await message.answer(greeting, reply_markup=build_home_reply_keyboard())

    if user is not None:
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

        await render_root_for_message(message, session, str(user.id))


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
    await state.update_data(flow_message_id=callback.message.message_id)

    try:
        text = build_section_text("💼 Создание бюджета", "Введите название")
        await callback.message.edit_text(
            text,
            reply_markup=build_first_run_back_keyboard(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await callback.message.answer(
            build_section_text("💼 Создание бюджета", "Введите название"),
            reply_markup=build_first_run_back_keyboard(),
            parse_mode="HTML",
        )
    await _safe_callback_answer(callback)




@router.callback_query(F.data == JOIN_BUDGET_CALLBACK)
async def join_budget_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(JoinBudgetStates.token)
    await state.update_data(flow_message_id=callback.message.message_id)
    try:
        text = build_section_text("🔗 Присоединиться", "Пришли ссылку или код вида invite_XXXX")
        await callback.message.edit_text(
            text,
            reply_markup=build_first_run_back_keyboard(),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await callback.message.answer(
            build_section_text("🔗 Присоединиться", "Пришли ссылку или код вида invite_XXXX"),
            reply_markup=build_first_run_back_keyboard(),
            parse_mode="HTML",
        )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == FIRST_RUN_BACK)
async def first_run_back(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
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
async def cancel_message(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
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


@router.message(F.text == HOME_REPLY_TEXT)
async def home_message(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
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


@router.callback_query(F.data == CANCEL_CALLBACK)
async def cancel_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
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


@router.message(CreateBudgetStates.name)
async def budget_name_step(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if (message.text or "").strip().casefold() in {"назад", HOME_REPLY_TEXT.casefold()}:
        await state.clear()
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
        return
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название не должно быть пустым. Попробуй ещё раз.")
        return
    await state.update_data(name=name)
    await state.set_state(CreateBudgetStates.base_currency)
    data = await state.get_data()
    msg_id = data.get("flow_message_id")
    text = build_section_text("💼 Создание бюджета", "Выберите базовую валюту")
    await _edit_flow_message(
        message,
        msg_id,
        text,
        reply_markup=build_base_currency_keyboard(),
        parse_mode="HTML",
    )


@router.message(JoinBudgetStates.token)
async def join_budget_token_step(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.from_user is None:
        await message.answer("Не нашёл пользователя. Попробуй /start ещё раз.")
        await state.clear()
        return
    text_raw = message.text or ""
    text = text_raw.strip()
    if text.casefold() in {"отмена", "назад", HOME_REPLY_TEXT.casefold()} or text.startswith(
        ("/start", "/main_menu", "/main-menu")
    ):
        await state.clear()
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
    data = await state.get_data()
    msg_id = data.get("flow_message_id")
    text = f'{owner_text} пригласил вас в совместный бюджет "{budget_name}".'
    await _edit_flow_message(
        message,
        msg_id,
        text,
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
    if user_id is not None:
        await render_root_for_callback(callback, session, user_id)
        return
    await callback.message.answer("✅ Ты присоединился к бюджету.")
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith(BASE_CURRENCY_PREFIX), CreateBudgetStates.base_currency)
async def budget_base_currency_step(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(BASE_CURRENCY_PREFIX, 1)[1].upper()
    if value not in BASE_CURRENCIES:
        await callback.answer()
        return
    await state.update_data(base_currency=value, aux_currency_1=None, aux_currency_2=None)
    await state.set_state(CreateBudgetStates.aux_currency_1)
    available = [c for c in BASE_CURRENCIES if c != value]
    await callback.message.edit_text(
        "Выберите до 2 дополнительных валют",
        reply_markup=build_aux_currency_keyboard(available, allow_skip=True),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(AUX_CURRENCY_PREFIX), CreateBudgetStates.aux_currency_1)
async def budget_aux_currency_pick(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(AUX_CURRENCY_PREFIX, 1)[1].upper()
    data = await state.get_data()
    base_currency = (data.get("base_currency") or "").upper()
    selected: list[str] = list(data.get("aux_currencies") or [])
    if value == base_currency or value not in BASE_CURRENCIES or value in selected:
        await callback.answer()
        return
    selected.append(value)
    available = [c for c in BASE_CURRENCIES if c != base_currency and c not in selected]
    await state.update_data(aux_currencies=selected)
    if len(selected) >= 2:
        await state.update_data(
            aux_currency_1=selected[0],
            aux_currency_2=selected[1] if len(selected) > 1 else None,
        )
        await state.set_state(CreateBudgetStates.timezone)
        await callback.message.edit_text(
            "Выберите таймзону",
            reply_markup=build_timezone_keyboard(),
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        "Выберите до 2 дополнительных валют",
        reply_markup=build_aux_currency_keyboard(available, allow_skip=True),
    )
    await callback.answer()


@router.callback_query(F.data == AUX_SKIP_CALLBACK, CreateBudgetStates.aux_currency_1)
async def budget_aux_currency_skip(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected: list[str] = list(data.get("aux_currencies") or [])
    await state.update_data(
        aux_currency_1=selected[0] if len(selected) > 0 else None,
        aux_currency_2=selected[1] if len(selected) > 1 else None,
    )
    await state.set_state(CreateBudgetStates.timezone)
    await callback.message.edit_text(
        "Выберите таймзону",
        reply_markup=build_timezone_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(TIMEZONE_PREFIX), CreateBudgetStates.timezone)
async def budget_timezone_step(callback: CallbackQuery, state: FSMContext) -> None:
    timezone = callback.data.split(TIMEZONE_PREFIX, 1)[1]
    await state.update_data(timezone=timezone)
    await _send_budget_summary_callback(callback, state)


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
    msg_id = data.get("flow_message_id")
    await _edit_flow_message(
        target,
        msg_id,
        text,
        reply_markup=build_confirm_inline_keyboard(),
    )


async def _send_budget_summary_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
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
    await callback.message.edit_text(text, reply_markup=build_confirm_inline_keyboard())
    await callback.answer()


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
    await render_root_for_callback(callback, session, owner_user_id)


@router.callback_query(F.data == "onboarding:edit_budget", CreateBudgetStates.confirm)
async def edit_budget(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateBudgetStates.timezone)
    await callback.message.edit_text(
        "Выберите таймзону",
        reply_markup=build_timezone_keyboard(),
    )
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return


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
