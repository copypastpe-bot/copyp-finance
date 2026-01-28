from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
