import logging.config

import msgpack

from my_app.matchmaker.handlers.match import handle_event_get_match
from my_app.matchmaker.logger import LOGGING_CONFIG, correlation_id_ctx, logger
from my_app.matchmaker.storage import rabbit
from my_app.shared.rabbit.matchmaking import MATCHES_QUEUE
from my_app.shared.schema.messages.match import MATCH_MESSAGE_EVENT, MatchMessage


async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info("Starting matchmaker")
    queue_name = MATCHES_QUEUE
    async with rabbit.channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    correlation_id_ctx.set(message.correlation_id)
                    body: MatchMessage = msgpack.unpackb(message.body)
                    if body["event"] == MATCH_MESSAGE_EVENT:
                        await handle_event_get_match(body)
