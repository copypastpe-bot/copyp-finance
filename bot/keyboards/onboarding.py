from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CREATE_BUDGET_CALLBACK = "onboarding:create_budget"
JOIN_BUDGET_CALLBACK = "onboarding:join_budget"
SKIP_AUX_CURRENCY = "onboarding:skip_aux"
USE_DEFAULT_TIMEZONE = "onboarding:default_tz"


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


def build_skip_aux_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data=SKIP_AUX_CURRENCY)]
        ]
    )


def build_default_timezone_keyboard(default_tz: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Оставить {default_tz}",
                    callback_data=USE_DEFAULT_TIMEZONE,
                )
            ]
        ]
    )
