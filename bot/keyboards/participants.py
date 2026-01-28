from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_participants_keyboard(participant_ids: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for participant_id in participant_ids:
        rows.append(
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"participants:remove:{participant_id}",
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
