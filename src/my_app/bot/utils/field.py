from typing import TypeVar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from my_app.bot.handlers.buttons import FieldCallback
from my_app.config.settings import settings
from my_app.shared.game.game_logic.core import Cell, GameObject, GameWorld
from my_app.shared.game.game_logic.game_objects import Bank, Castle, Warriors
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)
from my_app.shared.schema.messages.match import RoomCreatedMessage

T = TypeVar("T")


def get_type(game_object: GameObject | None) -> str:
    match game_object:
        case Castle():
            return "castle"
        case Bank():
            return "bank"
        case Warriors():
            return "warrior"
        case _:
            return "field"


def get_icon(game_object: GameObject | None, player_tag: int) -> str:
    if player_tag == 1:
        icons = settings.ICONSR
    else:
        icons = settings.ICONSB
    return icons[get_type(game_object)]


def rotate_clockwise(matrix: list[list[T]]) -> list[list[T]]:
    return list(zip(*matrix[::-1]))


def rotate_counterclockwise(matrix: list[list[T]]) -> list[list[T]]:
    return list(zip(*matrix))[::-1]


def rotate_field(field: list[list[Cell]], user_tag: int) -> list[list[Cell]]:
    if user_tag == 2:
        return rotate_clockwise(field)
    return rotate_counterclockwise(field)
