from uuid import UUID, uuid4

import aio_pika
import msgpack
from redis import Redis

from my_app.game.room_manager import create_room, send_command
from my_app.game.storage.rabbit import channel_pool
from my_app.shared.rabbit.matchmaking import USER_MATCH_EXCHANGE, USER_MATCH_QUEUE_KEY
from my_app.shared.schema.messages.match import CreateMatchMessage, RoomCreatedMessage
from my_app.shared.schema.redis.redis_keys import ROOM_KEY


async def handle_event_create_match(message: CreateMatchMessage):
    user_ids: list[int] = message["user_ids"]
    room_id: UUID = str(uuid4())
    print(F"ROOM UUID: {room_id}\ncreate room for user_ids: {user_ids}")

    game, game_world = create_room(room_id=room_id, user_id1=user_ids[0], user_id2=user_ids[1])

    for user_id in user_ids:
        queue_name = USER_MATCH_QUEUE_KEY.format(user_id=user_id)
        is_user_turn =  game.is_user_turn(user_id)
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
                    msgpack.packb(RoomCreatedMessage.create(
                        room_id=str(room_id),
                        game_world=game_world,
                        your_turn=is_user_turn
                    )),
                ),
                routing_key=queue_name
            )