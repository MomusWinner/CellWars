import aio_pika
import msgpack

from matchmaker.storage.rabbit import channel_pool
from shared.schema.messages.match import GetMatchMessage
from matchmaker.handlers.match import handle_event_get_match
from matchmaker.matchmaker import Matchmaker


async def send_test_data():
    queue_name = "matches"
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue(queue_name, durable=True)

        exchange = await channel.declare_exchange("match", aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb({
                    'event': 'get_match',
                    'user_id': 123,
                }),
            ),
            routing_key=queue_name,
        )


async def main() -> None:
    await send_test_data()
    await send_test_data()

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
