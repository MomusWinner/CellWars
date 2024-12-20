import aio_pika
import msgpack
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from my_app.bot.composables.actions import add_cancel_button, add_field_actions
from my_app.bot.composables.field import (
    render_available_bank_placements,
    render_available_warrior_placements,
    render_field,
)
from my_app.bot.handlers.buttons import (
    CANCEL_FIELD_INLINE,
    PLACE_BANK_INLINE,
    PLACE_WARRIORS_INLINE,
)
from my_app.bot.storage.rabbit import channel_pool
from my_app.bot.types.callbacks import PlacementCallback
from my_app.bot.types.game import GameTGMessage
from my_app.bot.utils.field import rotate_coordinates
from my_app.shared.game.game_logic.command import (
    BuildBank,
    BuyWarriorsCommand,
    PositionCommand,
    create_build_bank_command,
)
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)
from my_app.shared.rabbit.game import GAME_EXCHANGE, GAME_QUEUE
from my_app.shared.schema.messages.game import GameMessage, create_game_message

from .router import router


@router.callback_query(PLACE_WARRIORS_INLINE())
async def warrior_placement_intent_handler(
    callback_query: CallbackQuery,
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return

    game_message = GameTGMessage.from_markup(message.text, reply_markup)
    available_places = render_available_warrior_placements(game_message)

    game_message.actions = []
    with_cancel = add_cancel_button(available_places)

    await message.edit_reply_markup(reply_markup=with_cancel.export_markup())


@router.callback_query(PLACE_BANK_INLINE())
async def bank_placement_intent_handler(
    callback_query: CallbackQuery,
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return

    game_message = GameTGMessage.from_markup(message.text, reply_markup)
    available_places = render_available_bank_placements(game_message)

    game_message.actions = []
    with_cancel = add_cancel_button(available_places)

    await message.edit_reply_markup(reply_markup=with_cancel.export_markup())


@router.callback_query(CANCEL_FIELD_INLINE())
async def cancel_placement_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return

    data = await state.get_data()
    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)
    user_tag: int = data["user_tag"]

    field_buttons = render_field(game_world, user_tag)

    with_actions = add_field_actions(GameTGMessage.from_field(field_buttons))

    await message.edit_reply_markup(reply_markup=with_actions.export_markup())


@router.callback_query(PlacementCallback.filter(F.type == "bank"))
async def place_bank_handler(
    callback_query: CallbackQuery, callback_data: PlacementCallback, state: FSMContext
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    data = await state.get_data()
    room_id: str = data["room_id"]
    user_tag: int = data["user_tag"]

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return
    game_tg_message = GameTGMessage.from_markup(message.text, reply_markup)
    len_y = len(game_tg_message.field)
    len_x = len(game_tg_message.field[0])
    point = (callback_data.cell_y, callback_data.cell_x)
    point_rotated = rotate_coordinates(point, len_x, len_y, user_tag)
    position: PositionCommand = {"x": point_rotated[0], "y": point_rotated[1]}
    print(user_tag)
    print(position)

    channel: aio_pika.Channel
    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(GAME_QUEUE, durable=True)
        exchange = await channel.declare_exchange(GAME_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)
        game_message_dict = create_game_message(
            room_id=room_id,
            command=create_build_bank_command(user_id=callback_query.from_user.id, position=position),
        )

        body_exchange: bytes | None = msgpack.packb(game_message_dict)
        if body_exchange is None:
            return

        await exchange.publish(
            aio_pika.Message(
                body_exchange,
            ),
            routing_key=GAME_QUEUE,
        )
    await callback_query.answer()
