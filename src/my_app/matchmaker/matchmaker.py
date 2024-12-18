from asyncio import Lock

import aio_pika
import msgpack

from my_app.matchmaker.logger import logger
from my_app.matchmaker.storage import rabbit
from my_app.shared.rabbit.matchmaking import CREATE_MATCH_QUEUE, GAME_MATCH_EXCHANGE
from my_app.shared.schema.messages.match import create_create_match_message


class Matchmaker:
    def __init__(self) -> None:
        self._users_ids: list[int] = []
        self._users_lock = Lock()

    async def add_user(self, user_id: int) -> None:
        async with self._users_lock:
            self._users_ids.append(user_id)
        await self.create_match()

    async def remove_user(self, user_id: int) -> None:
        async with self._users_lock:
            if user_id in self._users_ids:
                self._users_ids.remove(user_id)
                logger.info("Remove User from matchmaker id: " + str(user_id))
            else:
                logger.warning("No user with this id(%s) was found", user_id)

    async def send_create_match_message(self, user_ids: list[int]) -> None:
        async with rabbit.channel_pool.acquire() as channel:
            queue = await channel.declare_queue(CREATE_MATCH_QUEUE, durable=True)
            exchange = await channel.declare_exchange(
                GAME_MATCH_EXCHANGE,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )
            await queue.bind(exchange)
            await exchange.publish(
                aio_pika.Message(
                    msgpack.packb(create_create_match_message(user_ids)),
                ),
                routing_key=CREATE_MATCH_QUEUE,
            )
            logger.info("Send create game match for users %s", user_ids)

    async def create_match(self) -> None:
        async with self._users_lock:
            while len(self._users_ids) >= 2:
                first_user = self._users_ids.pop()
                second_user = self._users_ids.pop()
                await self.send_create_match_message([first_user, second_user])
