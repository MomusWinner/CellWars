import aio_pika
import msgpack
from my_app.bot.storage.rabbit import channel_pool
from my_app.shared.schema.messages.base import BaseMessage


async def publish_message(dict: BaseMessage, queue_name: str, exchange_name: str) -> None:
    channel: aio_pika.Channel
    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(queue_name, durable=True)
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)
        body_exchange: bytes | None = msgpack.packb(dict)
        if body_exchange is None:
            return

        await exchange.publish(
            aio_pika.Message(
                body_exchange,
            ),
            routing_key=queue_name,
        )
