import logging.config
import aio_pika
import msgpack

from my_app.game.storage.redis import setup_redis
from my_app.game.handlers.match_queue_handler import handle_matches
from my_app.game.handlers.game_queue_handler import handle_games
from my_app.game.logger import logger, LOGGING_CONFIG

import asyncio

async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Starting game server...')
    setup_redis()
    await asyncio.gather(
        asyncio.create_task(handle_matches()),
        asyncio.create_task(handle_games())
    )