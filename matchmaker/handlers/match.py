
import aio_pika
import msgpack
from aio_pika import ExchangeType
from sqlalchemy import select, func

from config.settings import settings
# from matchmaker.model.gift import Gift
from shared.schema.messages.match import GetMatchMessage
from matchmaker.storage.db import async_session
from matchmaker.storage.rabbit import channel_pool
from matchmaker.matchmaker import Matchmaker

matchmaker: Matchmaker = Matchmaker()


async def handle_event_get_match(message: GetMatchMessage):
    print("get_message ", message)
    await matchmaker.add_user(message["user_id"])