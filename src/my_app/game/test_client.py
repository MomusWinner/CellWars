import asyncio

import aio_pika
import msgpack
from aio_pika.exceptions import QueueEmpty

from my_app.game.storage.rabbit import channel_pool
from my_app.shared.game.game_logic.serialize_deserialize_game_world import json_to_game_world
from my_app.shared.rabbit.game import GAME_EXCHANGE, GAME_INFO_QUEUE, GAME_QUEUE
from my_app.shared.rabbit.matchmaking import MATCHES_QUEUE, MATCHMAKER_MATCH_EXCHANGE, USER_MATCH_QUEUE_KEY
from my_app.shared.schema.messages.game import GameInfoMessage, GameMessage
from my_app.shared.schema.messages.match import MatchMessage, RoomCreatedMessage

user_id1 = 111
user_id2 = 222
room_id = ""


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


async def send_game_message(command, room_id):
    async with channel_pool.acquire() as channel:
            channel: aio_pika.Channel
            queue = await channel.declare_queue(GAME_QUEUE, durable=True)
            exchange = await channel.declare_exchange(
                GAME_EXCHANGE,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            await queue.bind(exchange)
            await exchange.publish(
                aio_pika.Message(
                    msgpack.packb(GameMessage.create(command=command, room_id=room_id)),
                ),
                routing_key=GAME_QUEUE,
            )


async def read_game_response(user_id):
    print(f"@--{user_id}: read message. QUEUE: {GAME_INFO_QUEUE}")
    queue_name = GAME_INFO_QUEUE.format(user_id=user_id)
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        retries = 3
        for _ in range(retries):
            try:
                message = await queue.get()
                async with message.process():
                    body: GameInfoMessage = msgpack.unpackb(message.body)
                    if body['event'] == GameInfoMessage.event:
                        print(f"  game_state: {body["game_state"]}")
                        print(f"  winner_id: {body["winner_id"]}")
                        print(f"  your_turn: ", body["your_turn"])
                        print(f"  exception_code: {body["exception_code"]}")
                        game_world = body["game_world"]
                        if game_world is not None:
                            game_world = json_to_game_world(body["game_world"])
                            game_world.print_cells()
            except QueueEmpty:
                await asyncio.sleep(1)
            else:
                break


async def read_match_create_response(user_id):
    print(f"@--{user_id}: read message. QUEUE: {USER_MATCH_QUEUE_KEY}")
    queue_name = USER_MATCH_QUEUE_KEY.format(user_id=user_id)
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        retries = 3
        for _ in range(retries):
            try:
                message = await queue.get()
                async with message.process():
                    body: RoomCreatedMessage = msgpack.unpackb(message.body)
                    if body['event'] == RoomCreatedMessage.event:
                        print("  your turn:", body["your_turn"])
                        print("  game_world:", body["game_world"] is not None)
                        print("  room_id:", body["room_id"])
            except QueueEmpty:
                await asyncio.sleep(1)
            else:
                break


async def run():
    await send_test_search_data(user_id1)
    await send_test_search_data(user_id2)
    room_id = input("room_id: ")
    await read_match_create_response(user_id1)
    await read_match_create_response(user_id2)

    command2 = {"command_name": "BUY_WARRIORS", "position":  {"x":1, "y":1}, "user_id":user_id2, "count": 1000}
    await send_game_message(command2, room_id)
    await read_game_response(user_id1)
    await read_game_response(user_id2)

    await asyncio.sleep(1)
    command = {"command_name": "BUY_WARRIORS", "position": {"x":1, "y":3}, "user_id":user_id1, "count": 10}
    await send_game_message(command, room_id)
    await read_game_response(user_id1)
    await read_game_response(user_id2)

    await asyncio.sleep(1)
    command2 = {"command_name": "MOVE_WARRIORS", "move_from":  {"x":1, "y":1}, "move_to":{"x":1, "y":3},"user_id":user_id2}
    await send_game_message(command2, room_id)
    await read_game_response(user_id1)
    await read_game_response(user_id2)


    await asyncio.sleep(1)
    command = {"command_name": "BUY_WARRIORS", "position": {"x":3, "y":3}, "user_id":user_id1, "count": 10}
    await send_game_message(command, room_id)
    await read_game_response(user_id1)
    await read_game_response(user_id2)


    await asyncio.sleep(1)
    command2 = {"command_name": "MOVE_WARRIORS", "move_from":  {"x":1, "y":3}, "move_to":{"x":2, "y":4},"user_id":user_id2}
    await send_game_message(command2, room_id)
    await read_game_response(user_id1)
    await read_game_response(user_id2)

asyncio.run(run())