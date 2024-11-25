import aio_pika
import msgpack
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from my_app.bot.composables.field import render_field
from my_app.bot.composables.info import game_info
from my_app.bot.handlers.buttons import CANCEL_MATCHMAKING_INLINE, MATCHMAKING_INLINE
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.handlers.states.menu import MenuGroup
from my_app.bot.replies.game import search_match
from my_app.bot.replies.menu import start_menu
from my_app.bot.storage.rabbit import channel_pool
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)
from my_app.shared.rabbit.matchmaking import (
    MATCHES_QUEUE,
    MATCHMAKER_MATCH_EXCHANGE,
    USER_MATCH_QUEUE_KEY,
)
from my_app.shared.schema.messages.match import MatchMessage, RoomCreatedMessage

from .router import router

channel: aio_pika.Channel


@router.callback_query(F.data == MATCHMAKING_INLINE["callback_data"])
async def start_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        raise Exception("Wrong type for the callback query message:", type(callback_query.message))

    await state.set_state(GameGroup.matchmaking)

    user_id = callback_query.from_user.id
    text, markup = search_match()

    await callback_query.message.edit_text(text, reply_markup=markup)
    await callback_query.answer()

    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(MATCHES_QUEUE, durable=True)
        exchange = await channel.declare_exchange(MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)
        await exchange.publish(
            aio_pika.Message(msgpack.packb(MatchMessage.create(user_id=user_id, action="search"))),
            routing_key=MATCHES_QUEUE,
        )

        user_queue = await channel.declare_queue(USER_MATCH_QUEUE_KEY.format(user_id=user_id), durable=True)
        async with user_queue.iterator() as user_queue_iter:
            async for message in user_queue_iter:
                async with message.process():
                    body: RoomCreatedMessage = msgpack.unpackb(message.body)
                    if body["your_turn"]:
                        await state.set_state(GameGroup.player_turn)
                    else:
                        await state.set_state(GameGroup.enemy_turn)
                    game_world = json_to_game_world(body["game_world"])
                    field_markup = render_field(game_world)
                    game_info_text = game_info(game_world, body["your_turn"])

                    await callback_query.message.edit_text(game_info_text, reply_markup=field_markup)
                    await state.update_data(room_id=body["room_id"])
                break


@router.callback_query(F.data == CANCEL_MATCHMAKING_INLINE["callback_data"])
async def cancel_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        raise Exception("Wrong type for the callback query message:", type(callback_query.message))

    await state.set_state(MenuGroup.start)
    text, markup = start_menu()
    user_id = callback_query.from_user.id

    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(MATCHES_QUEUE, durable=True)
        exchange = await channel.declare_exchange(MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)
        await exchange.publish(
            aio_pika.Message(msgpack.packb(MatchMessage.create(user_id=user_id, action="stop_search"))),
            routing_key=MATCHES_QUEUE,
        )

    await callback_query.message.edit_text(text, reply_markup=markup)
