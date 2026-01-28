from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.callback_data import encode_uuid


def build_budgets_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мои бюджеты", callback_data="budgets:menu:my")],
            [InlineKeyboardButton(text="Создать бюджет", callback_data="budgets:menu:create")],
            [InlineKeyboardButton(text="Присоединиться", callback_data="budgets:menu:join")],
            [InlineKeyboardButton(text="Закрыть", callback_data="budgets:menu:close")],
        ]
    )


def build_budgets_join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="budgets:menu:back"),
                InlineKeyboardButton(text="Закрыть", callback_data="budgets:menu:close"),
            ]
        ]
    )


def build_active_budget_keyboard(items: list[dict[str, str]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in items:
        rows.append(
            [
                InlineKeyboardButton(
                    text=item["name"],
                    callback_data=f"budgets:open:{item['budget_id']}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(text="Назад", callback_data="budgets:list:back"),
            InlineKeyboardButton(text="Закрыть", callback_data="budgets:close"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_budget_detail_keyboard(budget_id: str, can_set_default: bool) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="👥 Участники", callback_data=f"budget:participants:{budget_id}")],
        [InlineKeyboardButton(text="🔗 Пригласить участника", callback_data=f"budget:invite:{budget_id}")],
    ]
    if can_set_default:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⭐ Сделать по умолчанию",
                    callback_data=f"budget:set_default:{budget_id}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text="📦 Архивировать бюджет",
                callback_data=f"budget:archive:{budget_id}",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="budget:back"),
            InlineKeyboardButton(text="Закрыть", callback_data="budget:close"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_archive_confirm_keyboard(budget_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Архивировать", callback_data=f"budget:archive_confirm:{budget_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data=f"budget:archive_cancel:{budget_id}"
                ),
                InlineKeyboardButton(text="Закрыть", callback_data="budget:close"),
            ],
        ]
    )


def build_participants_keyboard(
    items: list[dict[str, str]], back_callback: str | None, budget_id: str | None
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in items:
        payload = encode_uuid(item["user_id"])
        if budget_id:
            payload = f"{encode_uuid(item['user_id'])}:{encode_uuid(budget_id)}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Удалить {item['username']}",
                    callback_data=f"p:rm:{payload}",
                )
            ]
        )
    if back_callback:
        rows.append(
            [
                InlineKeyboardButton(text="Назад", callback_data=back_callback),
                InlineKeyboardButton(text="Закрыть", callback_data="participants:close"),
            ]
        )
    else:
        rows.append([InlineKeyboardButton(text="Закрыть", callback_data="participants:close")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_confirm_remove_keyboard(
    participant_id: str, back_callback: str | None, budget_id: str | None
) -> InlineKeyboardMarkup:
    payload = encode_uuid(participant_id)
    if budget_id:
        payload = f"{encode_uuid(participant_id)}:{encode_uuid(budget_id)}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"p:cf:{payload}",
                )
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=back_callback or "participants:back"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="participants:cancel"),
                InlineKeyboardButton(text="Закрыть", callback_data="participants:close"),
            ],
        ]
    )
