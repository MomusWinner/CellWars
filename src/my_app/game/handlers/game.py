
import logging

import aio_pika
import msgpack

from my_app.game.room_manager import get_game, get_game_world_json, send_command
from my_app.game.storage.rabbit import channel_pool
from my_app.shared.game.game_logic.game_exceptions import GameException
from my_app.shared.game.game_logic.game_main import GameStates
from my_app.shared.game.game_logic.serialize_deserialize_game_world import get_game_world_json
from my_app.shared.rabbit.game import GAME_INFO_EXCHANGE, GAME_INFO_QUEUE
from my_app.shared.schema.messages.game import GameInfoMessage, GameMessage


async def handle_game_event(message: GameMessage) -> None:
    game_info: GameInfoMessage = None
    room_id = message["room_id"]
    game = get_game(room_id)
    if game is None:  # TODO
        logging.warning(f"room with id {room_id} is not defined in the room manager.")
        return

    try:
        game_state = send_command(room_id, message["command"])
    except GameException as ge:
        game_info = GameInfoMessage.create(game.game_state, exception_code=ge.exception_code)
    else:
        if game_state == GameStates.RUN.value:
            game_world = get_game_world_json(game.game_world)
            game_info = GameInfoMessage.create(game_state, game_world=game_world)
        elif game_state == GameStates.COMPLETE.value:
            winner_id = game.get_winner().user_id
            game_info = GameInfoMessage.create(game_state, winner_id=winner_id)
    
    if game_info is None:  # TODO
        logging.error(f"GAME_STATE {game.game_state} The game state was processed incorrectly.")
        return
    
    user_ids = list(game.user_id_to_team_tag.keys())

    if game_info["exception_code"] is not None:
        message_owner = message["command"]["user_id"]
        user_ids = [message_owner]

    user_id_turn = -1

    for user_id in user_ids:
        if game.is_user_turn(user_id):
            user_id_turn = user_id

    game_info["user_id_turn"] = user_id_turn
    game_info["your_tag"] = game.user_id_to_team_tag[user_id]
    queue_name = GAME_INFO_QUEUE
    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue(queue_name, durable=True)
        exchange = await channel.declare_exchange(
            GAME_INFO_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        await queue.bind(exchange)
        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(game_info)
            ),
            routing_key=queue_name
        )
