import asyncio
import logging
import uvicorn

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI

from config.settings import settings
from src.api.v1.router import router as v1_router
from src.storage.redis import setup_redis


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger')
    app.include_router(v1_router, prefix='/v1', tags=['v1'])

    return app

if __name__ == '__main__':
    if settings.BOT_WEBHOOK_URL:
        uvicorn.run('src.app:create_app', factory=True, host='0.0.0.0', port=8000, workers=1)
