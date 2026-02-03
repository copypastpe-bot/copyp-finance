from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

INCOME_SOURCES: list[tuple[str, str]] = [
    ("raketaclin", "Ракетаклин"),
    ("sveta", "Света"),
    ("rent", "Аренда квартиры"),
    ("dev", "Разработка"),
]

EXPENSE_CATEGORIES: list[tuple[str, str]] = [
    ("food", "Еда"),
    ("home", "Дом"),
    ("kids", "Ребенок"),
    ("travel", "Путешествия"),
]

BACK_TO_HOME = "nav:back:home"
BACK_TO_EXPENSE_AMOUNT = "nav:back:expense_amount"
BACK_TO_EXPENSE_CURRENCY = "nav:back:expense_currency"
BACK_TO_INCOME_AMOUNT = "nav:back:income_amount"
BACK_TO_INCOME_CURRENCY = "nav:back:income_currency"

EXPENSE_CURRENCY_PREFIX = "expense:currency:"
INCOME_CURRENCY_PREFIX = "income:currency:"
EXPENSE_CATEGORY_PREFIX = "expense:category:"
INCOME_SOURCE_PREFIX = "income:source:"

EXPENSE_CONFIRM = "expense:confirm"
EXPENSE_EDIT = "expense:edit"
INCOME_CONFIRM = "income:confirm"
INCOME_EDIT = "income:edit"

INCOME_REPEAT = "income:repeat"
INCOME_MORE = "income:more"
INCOME_DONE = "income:done"
EXPENSE_REPEAT = "expense:repeat"
EXPENSE_MORE = "expense:more"
EXPENSE_DONE = "expense:done"

GOALS_ROOT = "goals:root"
GOALS_CREATE = "goals:create"
GOALS_ADD = "goals:add"
GOALS_WITHDRAW = "goals:withdraw"
GOALS_LIST = "goals:list"

REPORTS_ROOT = "reports:root"
REPORTS_SUMMARY = "reports:summary"
REPORTS_OPERATIONS = "reports:operations"
REPORTS_GOALS = "reports:goals"


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Приход", callback_data="main:income"),
                InlineKeyboardButton(text="Расход", callback_data="main:expense"),
            ],
            [
                InlineKeyboardButton(text="Цели", callback_data="main:goals"),
                InlineKeyboardButton(text="Отчеты", callback_data="main:reports"),
            ],
        ]
    )


def build_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=callback_data)]]
    )


def build_currency_keyboard(
    currencies: list[str],
    prefix: str,
    back_callback: str,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for idx in range(0, len(currencies), 2):
        row = [
            InlineKeyboardButton(
                text=currencies[idx],
                callback_data=f"{prefix}{currencies[idx]}",
            )
        ]
        if idx + 1 < len(currencies):
            row.append(
                InlineKeyboardButton(
                    text=currencies[idx + 1],
                    callback_data=f"{prefix}{currencies[idx + 1]}",
                )
            )
        rows.append(row)
    rows.append([InlineKeyboardButton(text="Назад", callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_expense_currency_keyboard(currencies: list[str]) -> InlineKeyboardMarkup:
    return build_currency_keyboard(currencies, EXPENSE_CURRENCY_PREFIX, BACK_TO_EXPENSE_AMOUNT)


def build_income_currency_keyboard(currencies: list[str]) -> InlineKeyboardMarkup:
    return build_currency_keyboard(currencies, INCOME_CURRENCY_PREFIX, BACK_TO_INCOME_AMOUNT)


def build_expense_categories_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"{EXPENSE_CATEGORY_PREFIX}{key}")]
        for key, label in EXPENSE_CATEGORIES
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data=BACK_TO_EXPENSE_CURRENCY)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_income_sources_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"{INCOME_SOURCE_PREFIX}{key}")]
        for key, label in INCOME_SOURCES
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data=BACK_TO_INCOME_CURRENCY)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_confirm_keyboard(confirm_cb: str, edit_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data=confirm_cb)],
            [InlineKeyboardButton(text="Исправить", callback_data=edit_cb)],
        ]
    )


def build_done_keyboard(
    more_label: str,
    more_cb: str,
    repeat_cb: str,
    done_cb: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=more_label, callback_data=more_cb)],
            [InlineKeyboardButton(text="Повторить", callback_data=repeat_cb)],
            [InlineKeyboardButton(text="Готово", callback_data=done_cb)],
        ]
    )


def build_goals_root_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать цель", callback_data=GOALS_CREATE)],
            [InlineKeyboardButton(text="Пополнить", callback_data=GOALS_ADD)],
            [InlineKeyboardButton(text="Снять", callback_data=GOALS_WITHDRAW)],
            [InlineKeyboardButton(text="Список", callback_data=GOALS_LIST)],
            [InlineKeyboardButton(text="Назад", callback_data=BACK_TO_HOME)],
        ]
    )


def build_reports_root_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сводка", callback_data=REPORTS_SUMMARY)],
            [InlineKeyboardButton(text="Операции", callback_data=REPORTS_OPERATIONS)],
            [InlineKeyboardButton(text="Цели", callback_data=REPORTS_GOALS)],
            [InlineKeyboardButton(text="Назад", callback_data=BACK_TO_HOME)],
        ]
    )
