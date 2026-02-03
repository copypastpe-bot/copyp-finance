from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

SETTINGS_ROOT = "settings:root"
SETTINGS_BUDGETS = "settings:budgets"
SETTINGS_CURRENCIES = "settings:currencies"
SETTINGS_CATEGORIES = "settings:categories"

SETTINGS_BUDGETS_LIST = "settings:budgets:list"
SETTINGS_BUDGETS_ACTIVE = "settings:budgets:active"
SETTINGS_BUDGETS_PARTICIPANTS = "settings:budgets:participants"
SETTINGS_BUDGETS_INVITE = "settings:budgets:invite"

SETTINGS_CURRENCY_BASE = "settings:currency:base"
SETTINGS_CURRENCY_AUX_1 = "settings:currency:aux1"
SETTINGS_CURRENCY_AUX_2 = "settings:currency:aux2"

SETTINGS_CATEGORIES_EXPENSE = "settings:categories:expense"
SETTINGS_CATEGORIES_INCOME = "settings:categories:income"

SETTINGS_BACK = "settings:back"
SETTINGS_CANCEL = "settings:cancel"


def build_settings_root_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Бюджеты", callback_data=SETTINGS_BUDGETS)],
            [InlineKeyboardButton(text="Валюты", callback_data=SETTINGS_CURRENCIES)],
            [InlineKeyboardButton(text="Категории и источники", callback_data=SETTINGS_CATEGORIES)],
        ]
    )


def build_settings_back_cancel_keyboard(back_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=back_cb)],
            [InlineKeyboardButton(text="Отмена", callback_data=SETTINGS_CANCEL)],
        ]
    )


def build_settings_budgets_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Список бюджетов", callback_data=SETTINGS_BUDGETS_LIST)],
            [InlineKeyboardButton(text="Сменить активный", callback_data=SETTINGS_BUDGETS_ACTIVE)],
            [InlineKeyboardButton(text="Участники", callback_data=SETTINGS_BUDGETS_PARTICIPANTS)],
            [InlineKeyboardButton(text="Пригласить участника", callback_data=SETTINGS_BUDGETS_INVITE)],
            [InlineKeyboardButton(text="Назад", callback_data=SETTINGS_ROOT)],
            [InlineKeyboardButton(text="Отмена", callback_data=SETTINGS_CANCEL)],
        ]
    )


def build_settings_currencies_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Базовая валюта", callback_data=SETTINGS_CURRENCY_BASE)],
            [InlineKeyboardButton(text="Доп. валюта 1", callback_data=SETTINGS_CURRENCY_AUX_1)],
            [InlineKeyboardButton(text="Доп. валюта 2", callback_data=SETTINGS_CURRENCY_AUX_2)],
            [InlineKeyboardButton(text="Назад", callback_data=SETTINGS_ROOT)],
            [InlineKeyboardButton(text="Отмена", callback_data=SETTINGS_CANCEL)],
        ]
    )


def build_settings_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Категории расходов", callback_data=SETTINGS_CATEGORIES_EXPENSE)],
            [InlineKeyboardButton(text="Источники дохода", callback_data=SETTINGS_CATEGORIES_INCOME)],
            [InlineKeyboardButton(text="Назад", callback_data=SETTINGS_ROOT)],
            [InlineKeyboardButton(text="Отмена", callback_data=SETTINGS_CANCEL)],
        ]
    )
