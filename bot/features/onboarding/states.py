from aiogram.fsm.state import State, StatesGroup


class CreateBudgetStates(StatesGroup):
    name = State()
    base_currency = State()
    aux_currency_1 = State()
    aux_currency_2 = State()
    timezone = State()
    confirm = State()


class JoinBudgetStates(StatesGroup):
    token = State()
    confirm = State()
