from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить приход", callback_data="main:income"),
                InlineKeyboardButton(text="Добавить расход", callback_data="main:expense"),
            ],
            [
                InlineKeyboardButton(text="Цели", callback_data="main:goals"),
                InlineKeyboardButton(text="Бюджеты", callback_data="main:budgets"),
            ],
            [InlineKeyboardButton(text="Отчёты", callback_data="main:reports")],
        ]
    )
