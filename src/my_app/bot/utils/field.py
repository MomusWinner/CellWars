from typing import Any, TypeVar

from aiogram.types import InlineKeyboardButton

from my_app.bot.types.callbacks import FieldCallback, PlacementCallback
from my_app.config.settings import settings
from my_app.shared.game.game_logic.core import Cell, GameObject
from my_app.shared.game.game_logic.game_objects import Bank, Castle, Warriors

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
    zipped: list[tuple[T, ...]] = list(zip(*matrix[::-1]))
    return [list(row) for row in zipped]


def rotate_counterclockwise(matrix: list[list[T]]) -> list[list[T]]:
    zipped: list[tuple[T, ...]] = list(zip(*matrix))[::-1]
    return [list(row) for row in zipped]


def rotate_coordinates_clockwise(point: tuple[int, int], len_x: int) -> tuple[int, int]:
    return point[1], len_x - point[0] - 1


def rotate_coordinates_counterclockwise(point: tuple[int, int], len_y: int) -> tuple[int, int]:
    return len_y - point[1] - 1, point[0]


def rotate_field(field: list[list[Cell]], user_tag: int) -> list[list[Cell]]:
    if user_tag == 2:
        return rotate_clockwise(field)
    return rotate_counterclockwise(field)


def rotate_coordinates(point: tuple[int, int], game_field: list[list[Any]], user_tag: int) -> tuple[int, int]:
    len_x = len(game_field)
    len_y = len(game_field[0])
    if user_tag == 2:
        return rotate_coordinates_counterclockwise(point, len_y)
    return rotate_coordinates_clockwise(point, len_x)


def map_available_placements(
    buttons: list[list[InlineKeyboardButton]], type: str, places: list[str]
) -> list[list[InlineKeyboardButton]]:
    for y in range(len(buttons)):
        if y < 3:
            continue

        for x in range(len(buttons[y])):
            callback_data = buttons[y][x].callback_data
            if callback_data is None:
                raise Exception("no callback data")

            field_callback = FieldCallback.unpack(callback_data)
            if field_callback.type in places:
                continue

            icon = buttons[y][x].text + "🟢"

            buttons[y][x] = InlineKeyboardButton(
                text=icon,
                callback_data=PlacementCallback(
                    cell_x=field_callback.cell_x,
                    cell_y=field_callback.cell_y,
                    type=type,
                ).pack(),
            )
    return buttons
