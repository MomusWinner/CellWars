
from collections import deque
from typing import Any
from uuid import uuid4

import aio_pika
import msgpack
import pytest
import pytest_asyncio

from my_app.matchmaker.storage import rabbit

from .mocking.rabbitmq import (
    MockChannel,
    MockChannelPool,
    MockExchange,
    MockExchangeMessage,
    MockQueue,
)


@pytest.fixture()
def mock_exchange() -> MockExchange:
    return MockExchange()


@pytest_asyncio.fixture()
async def _load_queue(
    monkeypatch: pytest.MonkeyPatch,
    predefined_queue: list[Any],
    mock_exchange: MockExchange
) -> None:
    queue = MockQueue(deque())
    if predefined_queue is not None:
        for messages in predefined_queue:
            for message in messages:
                await queue.put(msgpack.packb(message), str(uuid4()))

    channel = MockChannel(queue=queue, exchange=mock_exchange)
    pool = MockChannelPool(channel=channel)
    monkeypatch.setattr(aio_pika, "Message", MockExchangeMessage)
    monkeypatch.setattr(rabbit, "connection_pool", None)
    monkeypatch.setattr(rabbit, "channel_pool", pool)
