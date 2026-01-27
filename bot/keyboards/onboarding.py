from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CREATE_BUDGET_CALLBACK = "onboarding:create_budget"
JOIN_BUDGET_CALLBACK = "onboarding:join_budget"


def build_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Создать бюджет", callback_data=CREATE_BUDGET_CALLBACK),
            ],
            [
                InlineKeyboardButton(text="➕ Присоединиться", callback_data=JOIN_BUDGET_CALLBACK),
            ],
        ]
    )
