import aio_pika
import msgpack

from my_app.game.handlers.game import handle_game_event
from my_app.game.storage.rabbit import channel_pool
from my_app.shared.rabbit.game import GAME_QUEUE
from my_app.shared.schema.messages.game import GAME_MESSAGE_EVENT, GameMessage


async def handle_games() -> None:
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(GAME_QUEUE, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body: GameMessage = msgpack.unpackb(message.body)
                    if body["event"] == GAME_MESSAGE_EVENT:
                        await handle_game_event(body)
