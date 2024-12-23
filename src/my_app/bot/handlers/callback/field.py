import aio_pika
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from my_app.bot.composables.actions import add_cancel_button
from my_app.bot.composables.info import game_info
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.types.callbacks import FieldCallback
from my_app.bot.types.game import GameTGMessage
from my_app.bot.types.renderers import BankRenderer, CastleRenderer, WarriorsRenderer

# from my_app.shared.game.game_logic.core import Player
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)

from .router import router

channel: aio_pika.Channel


@router.callback_query(FieldCallback.filter(), F.message.as_("message"), F.message.reply_markup.as_("reply_markup"))
async def field_handler(
    callback_query: CallbackQuery,
    callback_data: FieldCallback,
    state: FSMContext,
    message: Message,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    cell_x = callback_data.cell_x
    cell_y = callback_data.cell_y

    data = await state.get_data()
    state_str = await state.get_state()

    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)

    user_tag: int = data["user_tag"]
    game_message = GameTGMessage.from_markup(
        game_info(game_world, state_str == GameGroup.player_turn, user_tag),
        reply_markup,
    )

    match callback_data.type:
        case "castle":
            CastleRenderer(game_world, game_message).add_info(cell_x, cell_y, user_tag)
        case "warriors":
            warriors_renderer = WarriorsRenderer(game_world, game_message)
            warriors_renderer.add_info(cell_x, cell_y, user_tag)
            if state_str == GameGroup.player_turn:
                await state.update_data(warriors_place=(cell_y, cell_x))
                warriors_renderer.add_available_moves(cell_x, cell_y)
                add_cancel_button(game_message)
        case "bank":
            BankRenderer(game_world, game_message).add_info(cell_x, cell_y, user_tag)
        case _:
            return

    try:
        await message.edit_text(
            game_message.info,
            reply_markup=game_message.export_markup(),
        )
    finally:
        await callback_query.answer()
