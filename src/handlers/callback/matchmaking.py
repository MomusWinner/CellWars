import aio_pika
import msgpack

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F

from shared.schema.messages.match import MatchMessage, RoomIdMessage
from src.handlers.buttons import CANCEL_MATCHMAKING_INLINE, MATCHMAKING_INLINE, STATS_INLINE
from src.handlers.states.game import GameGroup
from src.handlers.states.menu import MenuGroup
from src.storage.rabbit import channel_pool
from shared.rabbit.matchmaking import MATCHES_QUEUE, MATCHMAKER_MATCH_EXCHANGE, USER_QUEUE_KEY

from .router import router


@router.callback_query(F.data == MATCHMAKING_INLINE["callback_data"])
async def start_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(GameGroup.matchmaking)
    await state.set_data({"message": callback_query.message.message_id})

    cancel = InlineKeyboardButton(
        text=CANCEL_MATCHMAKING_INLINE["text"], callback_data=CANCEL_MATCHMAKING_INLINE["callback_data"]
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[[cancel]])
    user_id = (callback_query.from_user.id,)

    await callback_query.message.edit_text("Ищем матч", reply_markup=markup)
    await callback_query.answer()

    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue(MATCHES_QUEUE, durable=True)

        exchange = await channel.declare_exchange(MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)

        await exchange.publish(
            aio_pika.Message(msgpack.packb(MatchMessage.create(user_id=user_id[0], action="search"))),
            routing_key=MATCHES_QUEUE,
        )

        user_queue = await channel.declare_queue(USER_QUEUE_KEY.format(user_id=user_id[0]), durable=True)
        async with user_queue.iterator() as user_queue_iter:
            async for message in user_queue_iter:
                async with message.process():
                    body: RoomIdMessage = msgpack.unpackb(message.body)
                    print(body)

                    await callback_query.message.edit_text(f"Under construction. Room ID: {body['room_id']}")

                    await state.update_data({"room_id": body["room_id"]})

                break


@router.callback_query(F.data == CANCEL_MATCHMAKING_INLINE["callback_data"])
async def cancel_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MenuGroup.start)
    matchmaking = InlineKeyboardButton(
        text=MATCHMAKING_INLINE["text"], callback_data=MATCHMAKING_INLINE["callback_data"]
    )
    stats = InlineKeyboardButton(text=STATS_INLINE["text"], callback_data=STATS_INLINE["callback_data"])
    markup = InlineKeyboardMarkup(inline_keyboard=[[matchmaking], [stats]])

    user_id = (callback_query.from_user.id,)

    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel

        queue = await channel.declare_queue(MATCHES_QUEUE, durable=True)

        exchange = await channel.declare_exchange(MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)

        await exchange.publish(
            aio_pika.Message(msgpack.packb(MatchMessage.create(user_id=user_id[0], action="stop_search"))),
            routing_key=MATCHES_QUEUE,
        )

    await callback_query.message.edit_text('Привет!', reply_markup=markup)
