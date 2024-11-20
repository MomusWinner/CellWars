from aiogram.fsm.state import StatesGroup, State


class GameGroup(StatesGroup):
    matchmaking = State()
    enemy_turn = State()
    player_turn = State()
