import aio_pika
import msgpack

from my_app.game.handlers.match import handle_event_create_match
from my_app.game.storage.rabbit import channel_pool
from my_app.shared.rabbit.matchmaking import CREATE_MATCH_QUEUE
from my_app.shared.schema.messages.match import CreateMatchMessage
<<<<<<< HEAD
=======

>>>>>>> dev


async def handle_matches() -> None:
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(CREATE_MATCH_QUEUE, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body: CreateMatchMessage = msgpack.unpackb(message.body)
                    if body["event"] == CreateMatchMessage.event:
                        await handle_event_create_match(body)
