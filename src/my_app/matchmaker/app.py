import aio_pika
import msgpack

from my_app.matchmaker.storage.rabbit import channel_pool
from my_app.shared.schema.messages.match import MatchMessage
from my_app.matchmaker.handlers.match import handle_event_get_match
from my_app.matchmaker.matchmaker import Matchmaker
from my_app.shared.rabbit.matchmaking import MATCHES_QUEUE, MATCHMAKER_MATCH_EXCHANGE
import logging.config
from my_app.matchmaker.logger import LOGGING_CONFIG, logger


async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Starting matchmaker')
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
