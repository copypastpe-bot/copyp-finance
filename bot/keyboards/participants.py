from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.callback_data import encode_uuid


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
