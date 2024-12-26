
from my_app.matchmaker.matchmaker import Matchmaker
from my_app.shared.schema.messages.match import MatchMessage

matchmaker: Matchmaker = Matchmaker()


async def handle_event_get_match(message: MatchMessage) -> None:
    if message["action"] == "search":
        await matchmaker.add_user(message["user_id"])
    elif message["action"] == "stop_search":
        await matchmaker.remove_user(message["user_id"])
