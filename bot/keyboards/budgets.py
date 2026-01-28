from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_active_budget_keyboard(items: list[dict[str, str]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in items:
        rows.append(
            [
                InlineKeyboardButton(
                    text=item["name"],
                    callback_data=f"budgets:set:{item['budget_id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="Закрыть", callback_data="budgets:close")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
