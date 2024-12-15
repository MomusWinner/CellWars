import aio_pika
import msgpack
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from my_app.bot.composables.actions import add_field_actions
from my_app.bot.composables.field import render_field
from my_app.bot.composables.info import game_info
from my_app.bot.handlers.buttons import CANCEL_MATCHMAKING_INLINE, MATCHMAKING_INLINE
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.handlers.states.menu import MenuGroup
from my_app.bot.replies.game import search_match
from my_app.bot.replies.menu import start_menu
from my_app.bot.storage.rabbit import channel_pool
from my_app.bot.types.game import GameMessage
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


@router.callback_query(MATCHMAKING_INLINE())
async def start_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        raise Exception(
            "Wrong type for the callback query message:", type(callback_query.message)
        )

    await state.set_state(GameGroup.matchmaking)

    user_id = callback_query.from_user.id
    text, markup = search_match()

    await callback_query.message.edit_text(text, reply_markup=markup)
    await callback_query.answer()
    await state.update_data(message_id=callback_query.message.message_id)
    await state.update_data(chat_id=callback_query.message.chat.id)

    channel: aio_pika.Channel
    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(MATCHES_QUEUE, durable=True)
        exchange = await channel.declare_exchange(
            MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True
        )

        await queue.bind(exchange)
        body_exchange: bytes | None = msgpack.packb(
            MatchMessage.create(user_id=user_id, action="search")
        )
        if body_exchange is None:
            return

        await exchange.publish(
            aio_pika.Message(body_exchange),
            routing_key=MATCHES_QUEUE,
        )


@router.callback_query(CANCEL_MATCHMAKING_INLINE())
async def cancel_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback_query.message, Message):
        raise Exception(
            "Wrong type for the callback query message:", type(callback_query.message)
        )

    await state.set_state(MenuGroup.start)
    text, markup = start_menu()
    user_id = callback_query.from_user.id

    channel: aio_pika.Channel
    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(MATCHES_QUEUE, durable=True)
        exchange = await channel.declare_exchange(
            MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True
        )

        await queue.bind(exchange)
        body_exchange: bytes | None = msgpack.packb(
            MatchMessage.create(user_id=user_id, action="stop_search")
        )
        if body_exchange is None:
            return

        await exchange.publish(
            aio_pika.Message(body_exchange),
            routing_key=MATCHES_QUEUE,
        )

    await callback_query.message.edit_text(text, reply_markup=markup)
