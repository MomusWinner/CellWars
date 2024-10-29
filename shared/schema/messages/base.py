from typing import TypedDict


class BaseMessage(TypedDict):
    event: str

    def create(event):
        return BaseMessage(event=event)