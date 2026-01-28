from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_budgets_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мои бюджеты", callback_data="budgets:menu:my")],
            [InlineKeyboardButton(text="Создать бюджет", callback_data="budgets:menu:create")],
            [InlineKeyboardButton(text="Присоединиться", callback_data="budgets:menu:join")],
            [InlineKeyboardButton(text="Назад", callback_data="budgets:menu:back")],
        ]
    )
