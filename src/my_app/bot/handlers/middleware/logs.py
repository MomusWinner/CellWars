import logging
from collections.abc import Awaitable
from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Update
from typing_extensions import override

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class LoggingMiddleware(BaseMiddleware):
    @override
    async def __call__(  # pyright: ignore[reportAny, reportIncompatibleMethodOverride]
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:

        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            user_message = event.data
        else:
            user_id = event.chat.id
            user_message = event.text

        state: FSMContext = data["state"]
        correlation_id: str = data["correlation_id"]
        update: Update = data["event_update"]

        logger.info(
            '{ "correlation_id": "%s", "update_id": %s, "user": %s, message: "%s", "state": { "context" : %s }',
            correlation_id,
            update.update_id,
            user_id,
            user_message,
            await state.get_state(),
        )

        await handler(event, data)
