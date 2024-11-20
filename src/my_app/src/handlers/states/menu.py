from aiogram.fsm.state import StatesGroup, State


class MenuGroup(StatesGroup):
    start = State()
    stats = State()
