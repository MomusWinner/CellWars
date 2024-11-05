
from config.settings import settings
from shared.schema.messages.match import MatchMessage
from matchmaker.storage.db import async_session
from matchmaker.storage.rabbit import channel_pool
from matchmaker.matchmaker import Matchmaker

matchmaker: Matchmaker = Matchmaker()


async def handle_event_get_match(message: MatchMessage):
    print("get_message ", message)
    if message["action"] == "search":
        await matchmaker.add_user(message["user_id"])
    elif message["action"] == "stop_search":
        await matchmaker.remove_user(message["user_id"])