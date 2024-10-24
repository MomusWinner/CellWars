import aio_pika
import msgpack

from matchmaker.storage.rabbit import channel_pool
from matchmaker.schema.match import GetMatchMessage
from matchmaker.handlers.match import handle_event_get_match

async def main() -> None:
    queue_name = "matches"
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body: GetMatchMessage = msgpack.unpackb(message.body)
                    if body['event'] == 'get_match':
                        await handle_event_get_match(body)
