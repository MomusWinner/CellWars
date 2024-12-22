from redis.asyncio import ConnectionPool, Redis

from my_app.config.settings import settings

redis: Redis


def setup_redis() -> Redis:
    global redis

    pool = ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    redis_ = Redis(connection_pool=pool)

    redis = redis_
    return redis_


def get_redis() -> Redis:
    global redis

    return redis
