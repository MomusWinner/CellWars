
from my_app.config.settings import settings
from my_app.shared.schema.messages.match import MatchMessage
from my_app.matchmaker.storage.db import async_session
from my_app.matchmaker.storage.rabbit import channel_pool
from my_app.matchmaker.matchmaker import Matchmaker

matchmaker: Matchmaker = Matchmaker()


async def handle_event_get_match(message: MatchMessage):
    if message["action"] == "search":
        await matchmaker.add_user(message["user_id"])
    elif message["action"] == "stop_search":
        await matchmaker.remove_user(message["user_id"])