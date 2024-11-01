import aio_pika
import msgpack

from matchmaker.storage.rabbit import channel_pool
from shared.schema.messages.match import MatchMessage
from matchmaker.handlers.match import handle_event_get_match
from matchmaker.matchmaker import Matchmaker
from shared.rabbit.matchmaking import MATCHES_QUEUE, MATCHMAKER_MATCH_EXCHANGE

async def send_test_search_data(user_id:str, action: str = "search"):
    queue_name = MATCHES_QUEUE
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue(queue_name, durable=True)

        exchange = await channel.declare_exchange(MATCHMAKER_MATCH_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)

        await queue.bind(exchange)

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(MatchMessage.create(action, user_id)),
            ),
            routing_key=queue_name,
        )


async def main() -> None:
    # await send_test_search_data(1) test matchmaking
    # await send_test_search_data(1, "stop_search")
    # await send_test_search_data(2)
    # await send_test_search_data(3)

    await send_test_search_data(2)
    await send_test_search_data(3)

    queue_name = MATCHES_QUEUE
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body: MatchMessage = msgpack.unpackb(message.body)
                    
                    if body['event'] == MatchMessage.event:
                        await handle_event_get_match(body)
