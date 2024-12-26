import time
from functools import wraps
from typing import Any, Callable, TypeVar

from prometheus_client import Counter, Histogram

BUCKETS = [
    0.2,
    0.4,
    0.6,
    0.8,
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0,
    float("+inf"),
]

INTEGRATION_METHOD_DURATION = Histogram(
    "bot_integration_method_duration_seconds",
    "Time spent in\
integration methods",
    buckets=BUCKETS,
)


BOT_MESSAGES_PRODUCED = Counter("bot_rabbitmq_messages_produced_total", "Total messages produced to RabbitMQ")
TURN_MESSAGES_CONSUMED = Counter("bot_turn_rabbitmq_messages_consumed_totals", "Total messages consumed from RabbitMQ")
MATCH_MESSAGES_CONSUMED = Counter(
    "bot_match_rabbitmq_messages_consumed_totals", "Total messages consumed from RabbitMQ"
)

REQUESTS_TOTAL = Counter("bot_http_requests_total", "Total HTTP Requests", ["status_code", "path"])

T = TypeVar("T")


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> T:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        INTEGRATION_METHOD_DURATION.observe(duration)
        return result

    return wrapper
