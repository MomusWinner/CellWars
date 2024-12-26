from collections.abc import Awaitable
from typing import Any, Callable
from uuid import uuid4

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from starlette_context import context
from starlette_context.header_keys import HeaderKeys
from typing_extensions import override

from my_app.config.settings import settings


class CorrelationIdMiddleware(BaseMiddleware):
    @override
    async def __call__(  # pyright: ignore[reportAny, reportIncompatibleMethodOverride]
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        if settings.BOT_WEBHOOK_URL:
            id = context.get(HeaderKeys.correlation_id)
        else:
            id = uuid4()

        data["correlation_id"] = id
        await handler(event, data)
