import asyncio
import logging.config

<<<<<<< HEAD
=======
import aio_pika
import msgpack

>>>>>>> dev
from my_app.game.handlers.game_queue_handler import handle_games
from my_app.game.handlers.match_queue_handler import handle_matches
from my_app.game.logger import LOGGING_CONFIG, logger
from my_app.game.storage.redis import setup_redis


async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info("Starting game server...")
    setup_redis()
    await asyncio.gather(
        asyncio.create_task(handle_matches()),
        asyncio.create_task(handle_games())
    )
