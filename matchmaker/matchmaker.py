import aio_pika
import msgpack

from shared.schema.messages.match import CreateMatchMessage
from matchmaker.storage.rabbit import channel_pool

from asyncio import Lock


class Matchmaker:
    def __init__(self):
        self._users_ids: list[int] = []
        self._users_lock = Lock()

    async def add_user(self, user_id: int):
        async with self._users_lock:
            self._users_ids.append(user_id)
        await self.create_match()

    async def send_create_match_message(self, user_ids: list[int]):
        queue_name = "create_matches"
        async with channel_pool.acquire() as channel:
            channel: aio_pika.Channel
            queue = await channel.declare_queue(queue_name, durable=True)
            exchange = await channel.declare_exchange("match", aio_pika.ExchangeType.DIRECT, durable=True)

            await queue.bind(exchange)
            await exchange.publish(
                aio_pika.Message(
                    msgpack.packb(CreateMatchMessage.create(user_ids)),
                ),
                routing_key=queue_name,
            )

    async def create_match(self):
        async with self._users_lock:
            while len(self._users_ids) >= 2:
                first_user = self._users_ids.pop()
                second_user = self._users_ids.pop()
                await self.send_create_match_message([first_user, second_user])
