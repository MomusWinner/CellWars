from aiogram.types import InlineKeyboardButton
from my_app.bot.handlers.buttons import FieldCallback
from my_app.bot.utils.field import rotate_field, get_icon, get_type
from my_app.shared.game.game_logic.core import GameWorld


def render_field(game_world: GameWorld, user_id: int) -> list[list[InlineKeyboardButton]]:
    field = rotate_field(game_world.cells, user_id)
    field_markup = []

    for row_idx, row in enumerate(field):
        markup_row = []
        for cell in range(len(row)):
            game_object = row[cell].game_object
            tag = 1
            if game_object is not None:
                tag = game_object.player.team_tag

            markup_row.append(
                InlineKeyboardButton(
                    text=get_icon(game_object, tag),
                    callback_data=FieldCallback(cell_x=cell, cell_y=row_idx, type=get_type(game_object)).pack(),
                )
            )
        field_markup.append(markup_row)
    return field_markup


# def render_available_moves(buttons: list[list[InlineKeyboardButton]], x: int, y: int) -> list[list[InlineKeyboardButton]]
# def render_available_warrior_placements(buttons: list[list[InlineKeyboardButton]], x: int, y: int) -> list[list[InlineKeyboardButton]]
# def render_available_bank_placements(buttons: list[list[InlineKeyboardButton]], x: int, y: int) -> list[list[InlineKeyboardButton]]
