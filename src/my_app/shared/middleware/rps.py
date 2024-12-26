from typing import Any, Callable

from fastapi import Request, Response
from prometheus_client import Counter


class RequestCountMiddleware:
    counter: Counter

    def __init__(self, counter: Counter) -> None:
        self.counter = counter

    async def __call__(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        response: Response = await call_next(request)
        self.counter.labels(status_code=response.status_code, path=request.url.path).inc()
        return response
