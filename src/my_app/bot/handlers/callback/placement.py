from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from my_app.bot.composables.actions import add_cancel_button, add_field_actions
from my_app.bot.composables.field import render_field
from my_app.bot.handlers.buttons import (
    CANCEL_FIELD_INLINE,
    PLACE_BANK_INLINE,
    PLACE_WARRIORS_INLINE,
)
from my_app.bot.handlers.states.game import PlacementGroup
from my_app.bot.types.callbacks import PlacementCallback
from my_app.bot.types.game import GameTGMessage
from my_app.bot.types.renderers import BankRenderer, WarriorsRenderer
from my_app.bot.utils.field import rotate_coordinates
from my_app.bot.utils.rabbit import publish_message
from my_app.shared.game.game_logic.command import PositionCommand, create_build_bank_command
from my_app.shared.game.game_logic.serialize_deserialize_game_world import json_to_game_world
from my_app.shared.rabbit.game import GAME_EXCHANGE, GAME_QUEUE
from my_app.shared.schema.messages.game import create_game_message

from .router import router


@router.callback_query(
    PLACE_WARRIORS_INLINE(),
    F.message.as_("message"),
    F.message.reply_markup.as_("reply_markup"),
    F.message.text.as_("text"),
)
async def warrior_placement_intent_handler(
    callback_query: CallbackQuery,
    message: Message,
    reply_markup: InlineKeyboardMarkup,
    text: str,
) -> None:
    game_message = GameTGMessage.from_markup(text, reply_markup)
    WarriorsRenderer(game_message).add_available_placements()

    game_message.actions = []
    add_cancel_button(game_message)

    await message.edit_reply_markup(reply_markup=game_message.export_markup())
    await callback_query.answer()


@router.callback_query(
    PLACE_BANK_INLINE(),
    F.message.as_("message"),
    F.message.reply_markup.as_("reply_markup"),
    F.message.text.as_("text"),
)
async def bank_placement_intent_handler(
    callback_query: CallbackQuery,
    message: Message,
    reply_markup: InlineKeyboardMarkup,
    text: str,
) -> None:
    game_message = GameTGMessage.from_markup(text, reply_markup)
    BankRenderer(game_message).add_available_placements()

    game_message.actions = []
    add_cancel_button(game_message)

    await message.edit_reply_markup(reply_markup=game_message.export_markup())
    await callback_query.answer()


@router.callback_query(CANCEL_FIELD_INLINE(), F.message.as_("message"))
async def cancel_placement_handler(
    callback_query: CallbackQuery,
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)
    user_tag: int = data["user_tag"]

    field_buttons = render_field(game_world, user_tag)

    with_actions = add_field_actions(GameTGMessage.from_field(field_buttons))

    await message.edit_reply_markup(reply_markup=with_actions.export_markup())
    await callback_query.answer()


@router.callback_query(PlacementCallback.filter(F.type == "warrior"), F.message.as_("message"))
async def place_warriors_handler(
    callback_query: CallbackQuery,
    callback_data: PlacementCallback,
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)
    user_tag: int = data["user_tag"]

    game_message = GameTGMessage.empty()
    WarriorsRenderer(game_message, game_world).add_count_info(user_tag)

    await message.edit_text(game_message.info, reply_markup=None)
    await state.set_state(PlacementGroup.warriors)
    await state.update_data(warrior_place=(callback_data.cell_y, callback_data.cell_x))
    await callback_query.answer()


@router.callback_query(
    PlacementCallback.filter(F.type == "bank"), F.message.reply_markup.as_("reply_markup"), F.message.text.as_("text")
)
async def place_bank_handler(
    callback_query: CallbackQuery,
    callback_data: PlacementCallback,
    state: FSMContext,
    reply_markup: InlineKeyboardMarkup,
    text: str,
    correlation_id: str,
) -> None:
    data = await state.get_data()

    room_id: str = data["room_id"]
    user_tag: int = data["user_tag"]

    game_tg_message = GameTGMessage.from_markup(text, reply_markup)

    point = (callback_data.cell_y, callback_data.cell_x)
    point_rotated = rotate_coordinates(point, game_tg_message.field, user_tag)
    position: PositionCommand = {"x": point_rotated[0], "y": point_rotated[1]}

    await publish_message(
        create_game_message(
            room_id=room_id,
            command=create_build_bank_command(user_id=callback_query.from_user.id, position=position),
        ),
        GAME_QUEUE,
        GAME_EXCHANGE,
        correlation_id,
    )

    await callback_query.answer()
