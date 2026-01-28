from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_budget_detail_keyboard(can_set_default: bool) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="👥 Участники", callback_data="budget:participants")],
        [InlineKeyboardButton(text="🔗 Пригласить участника", callback_data="budget:invite")],
    ]
    if can_set_default:
        rows.append(
            [InlineKeyboardButton(text="⭐ Сделать по умолчанию", callback_data="budget:set_default")]
        )
    rows.append(
        [InlineKeyboardButton(text="📦 Архивировать бюджет", callback_data="budget:archive")]
    )
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="budget:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_archive_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Архивировать", callback_data="budget:archive_confirm")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="budget:archive_cancel")],
        ]
    )
