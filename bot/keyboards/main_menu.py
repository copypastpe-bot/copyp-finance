from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить приход"), KeyboardButton(text="Добавить расход")],
            [KeyboardButton(text="Цели"), KeyboardButton(text="Бюджеты")],
            [KeyboardButton(text="Отчёты")],
        ],
        resize_keyboard=True,
    )
