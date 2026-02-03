from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

CANCEL_CALLBACK = "common:cancel"

CREATE_BUDGET_CALLBACK = "onboarding:create_budget"
JOIN_BUDGET_CALLBACK = "onboarding:join_budget"
INVITE_BUDGET_CALLBACK = "onboarding:invite_budget"
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
            [
                InlineKeyboardButton(text="🔗 Пригласить участника", callback_data=INVITE_BUDGET_CALLBACK),
            ],
            [
                InlineKeyboardButton(text="👥 Участники", callback_data="participants:list"),
            ],
            [
                InlineKeyboardButton(text="⭐ Активный бюджет", callback_data="budgets:active"),
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


def build_aux_currency_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить"), KeyboardButton(text="Назад"), KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_timezone_reply_keyboard(default_tz: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"Оставить {default_tz}")],
            [KeyboardButton(text="Назад"), KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Можно отменить",
    )


def build_cancel_back_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад"), KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Можно отменить",
    )


def build_home_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Главное меню")]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Главное меню",
    )


def build_confirm_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Создать бюджет", callback_data="onboarding:confirm_budget"),
            ],
            [
                InlineKeyboardButton(text="✏️ Исправить", callback_data="onboarding:edit_budget"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data=CANCEL_CALLBACK),
            ],
        ]
    )


def build_invite_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Присоединиться", callback_data="onboarding:accept_invite"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data=CANCEL_CALLBACK),
            ],
        ]
    )
