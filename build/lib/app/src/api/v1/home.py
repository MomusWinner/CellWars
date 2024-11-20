from fastapi import Depends
from fastapi.responses import JSONResponse, ORJSONResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .router import router
from my_app.bot.storage.db import get_db
from my_app.bot.storage.rabbit import channel_pool


@router.get("/home")
async def home(
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    return ORJSONResponse({"message": "Hello"})
