import asyncio
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from fastapi import FastAPI
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import (
    CorrelationIdPlugin,  # type: ignore[attr-defined, unused-ignore] # pyright: ignore[reportPrivateImportUsage]
)

from my_app.bot.api.tg.router import router as tg_router
from my_app.bot.api.v1.router import router as v1_router
from my_app.bot.bg_tasks import background_tasks
from my_app.bot.bot import setup_bot, setup_dp
from my_app.bot.handlers.callback.router import router as callback_router
from my_app.bot.handlers.command.router import router as command_router
from my_app.bot.handlers.message.router import router as message_router
from my_app.bot.handlers.middleware.correlation import CorrelationIdMiddleware
from my_app.bot.handlers.middleware.logs import LoggingMiddleware
from my_app.bot.listeners.game import listen_turns
from my_app.bot.listeners.matchmaking import listen_matches
from my_app.bot.logger import LOGGING_CONFIG, logger
from my_app.bot.storage.redis import get_redis, setup_redis
from my_app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info("Starting bot")

    setup_redis()
    redis = get_redis()
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(
        storage=storage,
        fsm_strategy=FSMStrategy.GLOBAL_USER,
    )

    setup_dp(dp)
    bot = Bot(token=settings.BOT_TOKEN)
    setup_bot(bot)

    dp.message.outer_middleware.register(CorrelationIdMiddleware())
    dp.callback_query.outer_middleware.register(CorrelationIdMiddleware())

    dp.message.outer_middleware.register(LoggingMiddleware())
    dp.callback_query.outer_middleware.register(LoggingMiddleware())

    dp.include_router(command_router)
    dp.include_router(message_router)
    dp.include_router(callback_router)
    await bot.delete_webhook()

    matches_task = asyncio.create_task(listen_matches(bot, storage))
    turns_task = asyncio.create_task(listen_turns(bot, storage))

    tasks = [matches_task, turns_task]

    if not settings.BOT_WEBHOOK_URL:
        polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
        tasks.append(polling_task)

    gathered_task = asyncio.gather(*tasks)

    await bot.set_webhook(settings.BOT_WEBHOOK_URL)
    yield

    gathered_task.cancel()
    while background_tasks:
        await asyncio.sleep(0)

    logging.getLogger("uvicorn").info("Ending lifespan")


def create_app() -> FastAPI:
    app = FastAPI(docs_url="/swagger", lifespan=lifespan)
    app.include_router(v1_router, prefix="/v1", tags=["v1"])
    app.include_router(tg_router, prefix="/tg", tags=["tg"])

    app.add_middleware(
        RawContextMiddleware, plugins=[CorrelationIdPlugin()]
    )  # pyright: ignore[reportPrivateImportUsage]
    return app


def start_bot() -> None:
    uvicorn.run("my_app.bot.app:create_app", factory=True, host="0.0.0.0", port=8000, workers=1)


if __name__ == "__main__":
    start_bot()
