import aio_pika
import msgpack

from my_app.shared.schema.messages.match import CreateMatchMessage
from my_app.shared.rabbit.matchmaking import CREATE_MATCH_QUEUE, GAME_MATCH_EXCHANGE
from my_app.matchmaker.storage.rabbit import channel_pool

from asyncio import Lock


class Matchmaker:
    def __init__(self):
        self._users_ids: list[int] = []
        self._users_lock = Lock()

    async def add_user(self, user_id: int):
        async with self._users_lock:
            self._users_ids.append(user_id)
        await self.create_match()

    async def remove_user(self, user_id: int):
        async with self._users_lock:
            if user_id in self._users_ids:
                self._users_ids.remove(user_id)
                print("remove User from matchmaker id: " + str(user_id))
            else:
                print(f"no user with this id({user_id}) was found")

    async def send_create_match_message(self, user_ids: list[int]):
        async with channel_pool.acquire() as channel:
            channel: aio_pika.Channel
            queue = await channel.declare_queue(CREATE_MATCH_QUEUE, durable=True)
            exchange = await channel.declare_exchange(
                GAME_MATCH_EXCHANGE,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            await queue.bind(exchange)
            await exchange.publish(
                aio_pika.Message(
                    msgpack.packb(CreateMatchMessage.create(user_ids)),
                ),
                routing_key=CREATE_MATCH_QUEUE,
            )

    async def create_match(self):
        async with self._users_lock:
            while len(self._users_ids) >= 2:
                first_user = self._users_ids.pop()
                second_user = self._users_ids.pop()
                await self.send_create_match_message([first_user, second_user])
