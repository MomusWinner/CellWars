import asyncio

from aiogram.types import Update
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

from my_app.bot.api.tg.router import router
from my_app.bot.bg_tasks import background_tasks
from my_app.bot.bot import get_bot, get_dp


@router.post("/webhook")
async def home_post(
    request: Request,
    # session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    data = await request.json()
    update = Update(**data)
    dp = get_dp()

    task = asyncio.create_task(dp.feed_webhook_update(get_bot(), update))
    background_tasks.add(task)

    return ORJSONResponse({"message": "Hello"})
