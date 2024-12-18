from aiogram.fsm.state import State, StatesGroup


class GameGroup(StatesGroup):
    matchmaking = State()
    enemy_turn = State()
    player_turn = State()
