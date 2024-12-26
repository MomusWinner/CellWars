from aiogram.fsm.state import State, StatesGroup


class MenuGroup(StatesGroup):
    start = State()
    stats = State()
