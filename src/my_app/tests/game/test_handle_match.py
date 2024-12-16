from typing import Any
import pytest
from my_app.shared.schema.messages.match import MatchMessage
from my_app.matchmaker.app import main
# from src.my_app.matchmaker.storage.rabbit import

@pytest.mark.parametrize(
    ("predefined_queue"),
    [
        (
            [
                MatchMessage.create("search", 111),
                MatchMessage.create("search", 222)
            ],
        ),
    ]
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures("_load_queue")
async def test_first(predefined_queue: list[Any]) -> None:
    await main()
    print("test")