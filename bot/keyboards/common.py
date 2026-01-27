from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

CANCEL_CALLBACK = "common:cancel"


def build_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Можно отменить",
    )


def build_confirm_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Создать бюджет", callback_data="onboarding:confirm_budget"),
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
                InlineKeyboardButton(text="▶️ Старт", callback_data="onboarding:accept_invite"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data=CANCEL_CALLBACK),
            ],
        ]
    )
