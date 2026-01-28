from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_participants_keyboard(
    items: list[dict[str, str]], back_callback: str | None, budget_id: str | None
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in items:
        payload = item["user_id"]
        if budget_id:
            payload = f"{item['user_id']}:{budget_id}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Удалить {item['username']}",
                    callback_data=f"participants:remove:{payload}",
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
    payload = participant_id
    if budget_id:
        payload = f"{participant_id}:{budget_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"participants:confirm:{payload}",
                )
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=back_callback or "participants:back"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="participants:cancel"),
                InlineKeyboardButton(text="Закрыть", callback_data="participants:close"),
            ],
        ]
    )
