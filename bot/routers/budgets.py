from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.budgets import build_active_budget_keyboard
from bot.keyboards.budget_detail import build_archive_confirm_keyboard, build_budget_detail_keyboard
from bot.keyboards.participants import build_confirm_remove_keyboard, build_participants_keyboard
from services.active_budget_service import (
    ActiveBudgetServiceError,
    get_active_budget_id,
    get_budget_detail,
    list_user_budgets,
    set_active_budget,
)
from services.invite_service import create_invite_for_owner
from services.participants_service import (
    ParticipantsServiceError,
    list_active_participants_for_budget,
    remove_participant_from_budget,
)
from services.user_service import ensure_user

router = Router()


@router.callback_query(F.data == "budgets:active")
async def active_budget_list(callback: CallbackQuery, session: AsyncSession) -> None:
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
    active_budget_id = await get_active_budget_id(session, user.id)
    items = await list_user_budgets(session, user.id)
    if not items:
        await callback.message.answer("Бюджетов нет.")
        await _safe_callback_answer(callback)
        return
    for item in items:
        if active_budget_id is not None and item["budget_id"] == str(active_budget_id):
            item["name"] = f"⭐ {item['name']}"
    await callback.message.answer(
        "Мои бюджеты:", reply_markup=build_active_budget_keyboard(items)
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budgets:close")
async def budgets_close(callback: CallbackQuery) -> None:
    from bot.keyboards.main_menu import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("budgets:open:"))
async def budgets_open(callback: CallbackQuery, session: AsyncSession) -> None:
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
    budget_id = callback.data.split("budgets:open:", 1)[1]
    try:
        budget = await get_budget_detail(session, user.id, uuid.UUID(budget_id))
    except ActiveBudgetServiceError as exc:
        await callback.message.answer(f"Не удалось открыть бюджет: {exc}")
        await _safe_callback_answer(callback)
        return

    active_budget_id = await get_active_budget_id(session, user.id)
    can_set_default = active_budget_id is None or str(active_budget_id) != budget_id
    await callback.message.answer(
        f"Бюджет: {budget.name}\nID:{budget.id}",
        reply_markup=build_budget_detail_keyboard(can_set_default),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:set_default")
async def budget_set_default(callback: CallbackQuery, session: AsyncSession) -> None:
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
    budget_id = _extract_budget_id(callback.message.text or "")
    if budget_id is None:
        await callback.message.answer("Не удалось определить бюджет.")
        await _safe_callback_answer(callback)
        return
    budget = await set_active_budget(session, user.id, budget_id)
    await callback.message.answer(f"Бюджет по умолчанию: {budget.name}")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:participants")
async def budget_participants(callback: CallbackQuery, session: AsyncSession) -> None:
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
    budget_id = _extract_budget_id(callback.message.text or "")
    if budget_id is None:
        await callback.message.answer("Не удалось определить бюджет.")
        await _safe_callback_answer(callback)
        return
    try:
        items = await list_active_participants_for_budget(session, user.id, budget_id)
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось открыть участников: {exc}")
        await _safe_callback_answer(callback)
        return
    if not items:
        await callback.message.answer("Участников нет.")
        await _safe_callback_answer(callback)
        return
    lines = ["👥 Участники\n"]
    keyboard_items: list[dict[str, str]] = []
    for item in items:
        lines.append(f"{item['username']} — {item['name']} ({item['role']})")
        if item["role"] != "владелец":
            keyboard_items.append(
                {"user_id": item["user_id"], "username": item["username"]}
            )
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=build_participants_keyboard(keyboard_items),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("participants:remove:"))
async def budget_participant_remove(callback: CallbackQuery, session: AsyncSession) -> None:
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
    participant_id = callback.data.split("participants:remove:", 1)[1]
    budget_id = _extract_budget_id(callback.message.text or "")
    if budget_id is None:
        await callback.message.answer("Не удалось определить бюджет.")
        await _safe_callback_answer(callback)
        return
    try:
        await callback.message.answer(
            "Удалить участника?",
            reply_markup=build_confirm_remove_keyboard(participant_id),
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
    await _safe_callback_answer(callback)


@router.callback_query(F.data.startswith("participants:confirm:"))
async def budget_participant_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
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
    participant_id = callback.data.split("participants:confirm:", 1)[1]
    budget_id = _extract_budget_id(callback.message.text or "")
    if budget_id is None:
        await callback.message.answer("Не удалось определить бюджет.")
        await _safe_callback_answer(callback)
        return
    try:
        await remove_participant_from_budget(
            session, user.id, budget_id, uuid.UUID(participant_id)
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer("✅ Участник удалён.")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:invite")
async def budget_invite(callback: CallbackQuery, session: AsyncSession) -> None:
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
            await callback.message.answer("Не удалось получить имя бота.")
            await _safe_callback_answer(callback)
            return
        link = f"https://t.me/{bot_username}?start=invite_{invite.token}"
        await callback.message.answer(
            "Готово 👇\n\n"
            f"Ссылка действует 24 часа и используется один раз:\n{link}"
        )
    except Exception as exc:
        await callback.message.answer(f"Не удалось создать приглашение: {exc}")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:archive")
async def budget_archive(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Архивировать бюджет?",
        reply_markup=build_archive_confirm_keyboard(),
    )
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:archive_cancel")
async def budget_archive_cancel(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:archive_confirm")
async def budget_archive_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
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
    budget_id = _extract_budget_id(callback.message.text or "")
    if budget_id is None:
        await callback.message.answer("Не удалось определить бюджет.")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer("Архивация будет добавлена позже.")
    await _safe_callback_answer(callback)


@router.callback_query(F.data == "budget:back")
async def budget_back(callback: CallbackQuery) -> None:
    from bot.keyboards.budgets_menu import build_budgets_menu_keyboard

    await callback.message.answer("Меню бюджетов:", reply_markup=build_budgets_menu_keyboard())
    await _safe_callback_answer(callback)


def _extract_budget_id(text: str) -> uuid.UUID | None:
    if not text.startswith("Бюджет: "):
        return None
    parts = text.split("ID:", 1)
    if len(parts) != 2:
        return None
    try:
        return uuid.UUID(parts[1].strip())
    except ValueError:
        return None


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return
