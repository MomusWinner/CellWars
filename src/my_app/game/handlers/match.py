from uuid import uuid4

import aio_pika
import msgpack

from my_app.game.logger import logger
from my_app.game.room_manager import create_room
from my_app.game.storage import rabbit
from my_app.shared.rabbit.matchmaking import USER_MATCH_EXCHANGE, USER_MATCH_QUEUE_KEY
from my_app.shared.schema.messages.match import CreateMatchMessage, create_room_created_message


async def handle_event_create_match(message: CreateMatchMessage) -> None:
    user_ids: list[int] = message["user_ids"]
    room_id = str(uuid4())
    logger.info("ROOM UUID: %s\ncreate room for user_ids: %s", room_id, str(user_ids))

    game, game_world = create_room(room_id=room_id, user_id1=user_ids[0], user_id2=user_ids[1])

    user_id_turn = -1

    for user_id in user_ids:
        if game.is_user_turn(user_id):
            user_id_turn = user_id

    queue_name = USER_MATCH_QUEUE_KEY
    async with rabbit.channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue(queue_name, durable=True)
        exchange = await channel.declare_exchange(USER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)
        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    create_room_created_message(room_id=str(room_id), game_world=game_world, user_id_turn=user_id_turn)
                ),
            ),
            routing_key=queue_name,
        )
