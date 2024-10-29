import aio_pika
import msgpack

from game.storage.rabbit import channel_pool
from game.storage.redis import setup_redis
from shared.schema.messages.match import CreateMatchMessage
from game.handlers.match import handle_event_create_match


async def handle_matches():
    queue_name = "create_matches"
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body: CreateMatchMessage = msgpack.unpackb(message.body)
                    if body['event'] == 'create_match':
                        await handle_event_create_match(body)

async def main() -> None:
    setup_redis()
    await handle_matches()
    # queue_name = "matches"
    # async with channel_pool.acquire() as channel:
    #     channel: aio_pika.Channel

    #     await channel.set_qos(prefetch_count=10)
    #     queue = await channel.declare_queue(queue_name, durable=True)

    #     async with queue.iterator() as queue_iter:
    #         async for message in queue_iter:
    #             async with message.process():
    #                 body: GetMatchMessage = msgpack.unpackb(message.body)
    #                 if body['event'] == 'get_match':
    #                     await handle_event_get_match(body)
