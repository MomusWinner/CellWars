import logging
import aio_pika
import msgpack
from my_app.game.storage import rabbit
from my_app.game.logger import logger
from my_app.game.room_manager import get_game, send_command
from my_app.shared.game.game_logic.game_exceptions import GameException
from my_app.shared.game.game_logic.game_main import GameStates
from my_app.shared.game.game_logic.serialize_deserialize_game_world import get_game_world_json
from my_app.shared.rabbit.game import GAME_INFO_EXCHANGE, GAME_INFO_QUEUE
from my_app.shared.schema.messages.game import GameInfoMessage, GameMessage, create_game_info_message


async def handle_game_event(message: GameMessage) -> None:
    game_info: GameInfoMessage | None = None
    room_id = message["room_id"]
    game = get_game(room_id)
    if game is None:
        logger.warning("Room with id %s is not defined in the room manager.", room_id)
        return

    try:
        game_state = send_command(room_id, message["command"])
    except GameException as ge:
        game_info = create_game_info_message(GameStates(game.game_state), exception_code=ge.exception_code)
    else:
        if game_state.value == GameStates.RUN.value:
            game_world = get_game_world_json(game.game_world)
            game_info = create_game_info_message(game_state, game_world=game_world)
        elif game_state.value == GameStates.COMPLETE.value:
            winner_id = game.get_winner()
            if winner_id is None:
                logger.error("Winner id is none while handling complete game state :(")
                return
            game_info = create_game_info_message(game_state, winner_id=winner_id.user_id)

    if game_info is None:
        logger.error("GAME_STATE %s The game state was processed incorrectly.", game.game_state)
        return

    user_ids = list(game.user_id_to_team_tag.keys())

    if game_info["exception_code"] is not None:
        message_owner = message["command"]["user_id"]
        user_ids = [message_owner]

    for user_id in user_ids:
        if game.is_user_turn(user_id):
            user_id_turn = user_id

    game_info["user_id_turn"] = user_id_turn
    queue_name = GAME_INFO_QUEUE
    async with rabbit.channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue(queue_name, durable=True)
        exchange = await channel.declare_exchange(GAME_INFO_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)
        await queue.bind(exchange)
        await exchange.publish(aio_pika.Message(msgpack.packb(game_info)), routing_key=queue_name)
