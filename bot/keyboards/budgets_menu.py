from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_budgets_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои бюджеты")],
            [KeyboardButton(text="Создать бюджет"), KeyboardButton(text="Присоединиться")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )
