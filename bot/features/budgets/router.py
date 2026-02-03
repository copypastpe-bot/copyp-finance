import uuid

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.features.budgets.keyboards import (
    build_active_budget_keyboard,
    build_archive_confirm_keyboard,
    build_budget_detail_keyboard,
    build_budgets_join_keyboard,
    build_budgets_menu_keyboard,
    build_confirm_remove_keyboard,
    build_participants_keyboard,
)
from bot.features.onboarding.keyboards import build_home_reply_keyboard
from bot.features.onboarding.states import CreateBudgetStates, JoinBudgetStates
from bot.utils.callback_data import decode_uuid
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
    get_participant_display,
    list_active_participants,
    list_active_participants_for_budget,
    remove_participant,
    remove_participant_from_budget,
)
from services.user_service import ensure_user

participants_router = Router()
budgets_router = Router()
router = Router()
router.include_router(participants_router)
router.include_router(budgets_router)


@participants_router.callback_query(F.data == "participants:list")
async def participants_list(callback: CallbackQuery, session: AsyncSession) -> None:
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
        items = await list_active_participants(session, user.id)
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

    text = "\n".join(lines)
    await callback.message.answer(
        text, reply_markup=build_participants_keyboard(keyboard_items, None, None)
    )
    await _safe_callback_answer(callback)


@participants_router.callback_query(F.data.startswith("p:rm:"))
async def participants_remove(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    payload = callback.data.split("p:rm:", 1)[1]
    if ":" in payload:
        payload = payload.split(":", 1)[0]
    participant_id = decode_uuid(payload)
    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    try:
        display = await get_participant_display(
            session, user.id, uuid.UUID(participant_id)
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer(
        f"Удалить участника?\n{display}",
        reply_markup=build_confirm_remove_keyboard(str(participant_id), None, None),
    )
    await _safe_callback_answer(callback)


@participants_router.callback_query(F.data.startswith("p:cf:"))
async def participants_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    payload = callback.data.split("p:cf:", 1)[1]
    if ":" in payload:
        payload = payload.split(":", 1)[0]
    participant_id = decode_uuid(payload)
    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    try:
        await remove_participant(
            session,
            user.id,
            participant_id,
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await callback.message.answer("✅ Участник удалён.")
    await _safe_callback_answer(callback)


@participants_router.callback_query(F.data == "participants:close")
async def participants_close(callback: CallbackQuery) -> None:
    from bot.features.main_menu.keyboards import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


@participants_router.callback_query(F.data == "participants:cancel")
async def participants_cancel(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:active")
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
        await _edit_or_answer(callback, "Бюджетов нет.")
        await _safe_callback_answer(callback)
        return
    for item in items:
        if active_budget_id is not None and item["budget_id"] == str(active_budget_id):
            item["name"] = f"⭐ {item['name']}"
    await _edit_or_answer(
        callback,
        "Мои бюджеты:",
        reply_markup=build_active_budget_keyboard(items),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:menu:my")
async def budgets_menu_my(callback: CallbackQuery, session: AsyncSession) -> None:
    await active_budget_list(callback, session)


@budgets_router.callback_query(F.data == "budgets:menu:create")
async def budgets_menu_create(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
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
    await state.update_data(owner_user_id=str(user.id))
    await state.set_state(CreateBudgetStates.name)
    await callback.message.answer(
        "Как назовём бюджет?",
        reply_markup=build_home_reply_keyboard(),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:menu:join")
async def budgets_menu_join(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(JoinBudgetStates.token)
    await _edit_or_answer(
        callback,
        "Пришли инвайт-ссылку или код приглашения.",
        reply_markup=build_budgets_join_keyboard(),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:menu:back")
async def budgets_menu_back(callback: CallbackQuery) -> None:
    from bot.features.main_menu.keyboards import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:menu:close")
async def budgets_menu_close(callback: CallbackQuery) -> None:
    from bot.features.main_menu.keyboards import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:close")
async def budgets_close(callback: CallbackQuery) -> None:
    from bot.features.main_menu.keyboards import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budgets:list:back")
async def budgets_list_back(callback: CallbackQuery) -> None:
    await _edit_or_answer(
        callback,
        "Меню бюджетов:",
        reply_markup=build_budgets_menu_keyboard(),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budgets:open:"))
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
    await _edit_or_answer(
        callback,
        f"Бюджет: {budget.name}\nID:{budget.id}",
        reply_markup=build_budget_detail_keyboard(str(budget.id), can_set_default),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budget:set_default:"))
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
    budget_id = callback.data.split("budget:set_default:", 1)[1]
    budget = await set_active_budget(session, user.id, uuid.UUID(budget_id))
    await _edit_or_answer(callback, f"Бюджет по умолчанию: {budget.name}")
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budget:participants:"))
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
    budget_id = callback.data.split("budget:participants:", 1)[1]
    try:
        items = await list_active_participants_for_budget(session, user.id, budget_id)
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось открыть участников: {exc}")
        await _safe_callback_answer(callback)
        return
    if not items:
        await _edit_or_answer(callback, "Участников нет.")
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
    await _edit_or_answer(
        callback,
        "\n".join(lines),
        reply_markup=build_participants_keyboard(
            keyboard_items, f"budget:back:{budget_id}", budget_id
        ),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("p:rm:"))
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
    payload = callback.data.split("p:rm:", 1)[1]
    if ":" not in payload:
        await _edit_or_answer(callback, "Не удалось определить участника.")
        await _safe_callback_answer(callback)
        return
    participant_part, budget_part = payload.split(":", 1)
    participant_id = decode_uuid(participant_part)
    budget_id = decode_uuid(budget_part)
    try:
        await _edit_or_answer(
            callback,
            "Удалить участника?",
            reply_markup=build_confirm_remove_keyboard(
                str(participant_id), f"budget:back:{budget_id}", str(budget_id)
            ),
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("p:cf:"))
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
    payload = callback.data.split("p:cf:", 1)[1]
    if ":" not in payload:
        await _edit_or_answer(callback, "Не удалось определить участника.")
        await _safe_callback_answer(callback)
        return
    participant_part, budget_part = payload.split(":", 1)
    participant_id = decode_uuid(participant_part)
    budget_id = decode_uuid(budget_part)
    try:
        await remove_participant_from_budget(
            session, user.id, budget_id, participant_id
        )
    except ParticipantsServiceError as exc:
        await callback.message.answer(f"Не удалось удалить: {exc}")
        await _safe_callback_answer(callback)
        return
    await _edit_or_answer(callback, "✅ Участник удалён.")
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budget:invite:"))
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
            await _edit_or_answer(callback, "Не удалось получить имя бота.")
            await _safe_callback_answer(callback)
            return
        link = f"https://t.me/{bot_username}?start=invite_{invite.token}"
        await _edit_or_answer(
            callback,
            "Готово 👇\n\n"
            f"Ссылка действует 24 часа и используется один раз:\n{link}",
        )
    except Exception as exc:
        await callback.message.answer(f"Не удалось создать приглашение: {exc}")
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budget:archive:"))
async def budget_archive(callback: CallbackQuery) -> None:
    budget_id = callback.data.split("budget:archive:", 1)[1]
    await _edit_or_answer(
        callback,
        "Архивировать бюджет?",
        reply_markup=build_archive_confirm_keyboard(budget_id),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budget:archive_cancel:"))
async def budget_archive_cancel(callback: CallbackQuery) -> None:
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data.startswith("budget:archive_confirm:"))
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
    budget_id = callback.data.split("budget:archive_confirm:", 1)[1]
    await _edit_or_answer(callback, "Архивация будет добавлена позже.")
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budget:back")
async def budget_back(callback: CallbackQuery, session: AsyncSession) -> None:
    await active_budget_list(callback, session)


@budgets_router.callback_query(F.data.startswith("budget:back:"))
async def budget_back_to_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user is None:
        await _safe_callback_answer(callback)
        return
    budget_id = callback.data.split("budget:back:", 1)[1]
    user = await ensure_user(
        session=session,
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    try:
        budget = await get_budget_detail(session, user.id, uuid.UUID(budget_id))
    except ActiveBudgetServiceError as exc:
        await callback.message.answer(f"Не удалось открыть бюджет: {exc}")
        await _safe_callback_answer(callback)
        return
    active_budget_id = await get_active_budget_id(session, user.id)
    can_set_default = active_budget_id is None or str(active_budget_id) != budget_id
    await _edit_or_answer(
        callback,
        f"Бюджет: {budget.name}\nID:{budget.id}",
        reply_markup=build_budget_detail_keyboard(str(budget.id), can_set_default),
    )
    await _safe_callback_answer(callback)


@budgets_router.callback_query(F.data == "budget:close")
async def budget_close(callback: CallbackQuery) -> None:
    from bot.features.main_menu.keyboards import build_main_menu_keyboard

    await callback.message.answer("Главное меню:", reply_markup=build_main_menu_keyboard())
    await _safe_callback_answer(callback)


async def _safe_callback_answer(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except TelegramBadRequest:
        return


async def _edit_or_answer(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=reply_markup)
