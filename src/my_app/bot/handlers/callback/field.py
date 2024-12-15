import aio_pika
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# from my_app import game
from my_app.bot.composables.info import game_info
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.types.callbacks import FieldCallback
from my_app.bot.utils.field import rotate_field

# from my_app.shared.game.game_logic.core import Player
from my_app.shared.game.game_logic.game_objects import Castle
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)

from .router import router

channel: aio_pika.Channel

# WARRIOR_TEXT = "Воин:\n  Тип: {type}\n  Колличество: {quantity}"
# @router.callback_query(FieldCallback.filter(F.type = "warrior"))
# async def warrior_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
#     cell = FieldCallback.unpack(callback_query.data)

CASTLE_TEXT = "\nВыбран Замок:\n  Тип: {type}\n  ХП: {hp}"


@router.callback_query(FieldCallback.filter(F.type == "castle"), GameGroup.player_turn)
async def castle_handler(
    callback_query: CallbackQuery, callback_data: FieldCallback, state: FSMContext
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    user_id = callback_query.from_user.id

    cell_x = callback_data.cell_x
    cell_y = callback_data.cell_y

    data = await state.get_data()
    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)
    user_tag: int = data["user_tag"]
    users_field = rotate_field(game_world.cells, user_tag)
    castle = users_field[cell_y][cell_x].game_object
    if not isinstance(castle, Castle):
        await callback_query.answer("oh")
        return

    player = castle.player

    if player.user_id == user_id:
        type = "Союзник"
    else:
        type = "Вражеский"

    await message.edit_text(
        game_info(game_world, True) + CASTLE_TEXT.format(type=type, hp=castle.hp),
        reply_markup=message.reply_markup,
    )
    await callback_query.answer()


@router.callback_query(FieldCallback.filter(), GameGroup.enemy_turn)
async def wrong_turn_handler(callback_query: CallbackQuery):
    await callback_query.answer("Not your turn")
