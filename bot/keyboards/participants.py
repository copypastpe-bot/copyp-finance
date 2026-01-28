from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_participants_keyboard(items: list[dict[str, str]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in items:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Удалить {item['username']}",
                    callback_data=f"participants:remove:{item['user_id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="Закрыть", callback_data="participants:close")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_confirm_remove_keyboard(participant_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"participants:confirm:{participant_id}",
                )
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="participants:cancel")],
        ]
    )
