from aiogram.fsm.state import State, StatesGroup


class ExpenseStates(StatesGroup):
    amount = State()
    currency = State()
    category = State()
    confirm = State()


class IncomeStates(StatesGroup):
    amount = State()
    currency = State()
    source = State()
    confirm = State()
