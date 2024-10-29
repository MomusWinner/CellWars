from redis import Redis
from shared.schema.messages.match import CreateMatchMessage
from game.storage.redis import get_redis
from uuid import uuid4, UUID

async def handle_event_create_match(message: CreateMatchMessage):
    user_ids: list[int] = message["user_ids"]
    print("create room for user_ids ", user_ids)
    room_id: UUID = uuid4()
    redis: Redis = get_redis()
    await redis.json().set(str(room_id), "$", {"test": "test_room"})
    ## create room
