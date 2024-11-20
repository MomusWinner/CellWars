from typing import TypedDict


class BaseCell(TypedDict):
    position: int
    character: str
    amount: int
