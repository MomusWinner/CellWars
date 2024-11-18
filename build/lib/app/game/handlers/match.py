from redis import Redis
from shared.schema.messages.match import CreateMatchMessage, RoomIdMessage
from game.storage.redis import get_redis
from uuid import uuid4, UUID
from shared.schema.redis.redis_keys import ROOM_KEY
from game.storage.rabbit import channel_pool
from shared.rabbit.matchmaking import USER_QUEUE_KEY, USER_MATCH_EXCHANGE
from game.game_logic.game_main import Game

import aio_pika
import msgpack


async def handle_event_create_match(message: CreateMatchMessage):
    user_ids: list[int] = message["user_ids"]
    print("create room for user_ids ", user_ids)
    room_id: UUID = uuid4()
    redis: Redis = get_redis()
    await redis.json().set(ROOM_KEY.format(room_id=str(room_id)), "$", Game())
    test_js = await redis.json().get(ROOM_KEY.format(room_id=str(room_id)))
    print(test_js)

    for user_id in user_ids:
        queue_name = USER_QUEUE_KEY.format(user_id=user_id)
        async with channel_pool.acquire() as channel:
            channel: aio_pika.Channel
            queue = await channel.declare_queue(queue_name, durable=True)
            exchange = await channel.declare_exchange(
                USER_MATCH_EXCHANGE,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            await queue.bind(exchange)
            await exchange.publish(
                aio_pika.Message(
                    msgpack.packb(RoomIdMessage.create(room_id=str(room_id))),
                ),
                routing_key=queue_name,)