from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

CANCEL_CALLBACK = "common:cancel"
HOME_REPLY_TEXT = "🏠 Home"
FIRST_RUN_BACK = "onboarding:back:first_run"
BASE_CURRENCY_PREFIX = "onboarding:base_currency:"
AUX_CURRENCY_PREFIX = "onboarding:aux_currency:"
AUX_SKIP_CALLBACK = "onboarding:aux_skip"
TIMEZONE_PREFIX = "onboarding:timezone:"

BASE_CURRENCIES = ["RSD", "RUB", "EUR", "USD"]
TIMEZONE_CHOICES = [
    ("Europe/Moscow", "Moscow"),
    ("Europe/Belgrade", "Belgrade"),
]

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
        keyboard=[[KeyboardButton(text=HOME_REPLY_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Home",
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


def build_first_run_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Создать бюджет", callback_data=CREATE_BUDGET_CALLBACK)],
            [InlineKeyboardButton(text="➕ Присоединиться", callback_data=JOIN_BUDGET_CALLBACK)],
        ]
    )


def build_first_run_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=FIRST_RUN_BACK)]]
    )


def build_base_currency_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for idx in range(0, len(BASE_CURRENCIES), 2):
        row = [
            InlineKeyboardButton(
                text=BASE_CURRENCIES[idx],
                callback_data=f"{BASE_CURRENCY_PREFIX}{BASE_CURRENCIES[idx]}",
            )
        ]
        if idx + 1 < len(BASE_CURRENCIES):
            row.append(
                InlineKeyboardButton(
                    text=BASE_CURRENCIES[idx + 1],
                    callback_data=f"{BASE_CURRENCY_PREFIX}{BASE_CURRENCIES[idx + 1]}",
                )
            )
        rows.append(row)
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def build_aux_currency_keyboard(
    available: list[str],
    allow_skip: bool,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=currency,
                callback_data=f"{AUX_CURRENCY_PREFIX}{currency}",
            )
        ]
        for currency in available
    ]
    if allow_skip:
        rows.append([InlineKeyboardButton(text="Пропустить", callback_data=AUX_SKIP_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_timezone_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"{TIMEZONE_PREFIX}{value}",
                )
            ]
            for value, label in TIMEZONE_CHOICES
        ]
    )
