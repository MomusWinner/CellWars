
import aio_pika
import msgpack
from aio_pika import ExchangeType
from sqlalchemy import select, func

from config.settings import settings
# from matchmaker.model.gift import Gift
from matchmaker.schema.match import GetMatchMessage
from matchmaker.storage.db import async_session
from matchmaker.storage.rabbit import channel_pool


def handle_event_get_match(message: GetMatchMessage):
    pass