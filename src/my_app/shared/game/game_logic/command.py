from dataclasses import dataclass
from typing import TypedDict


class PositionCommand(TypedDict):
    x: int
    y: int


@dataclass
class GameCommand:
    user_id: int
    command_name: str


class MoveWarriorsCommand(GameCommand):
    command_name = "MOVE_WARRIORS"
    move_from: PositionCommand
    move_to: PositionCommand


class BuyWarriorsCommand(GameCommand):
    command_name = "BUY_WARRIORS"
    position: PositionCommand
    count: int


class BuildBank(GameCommand):
    command_name = "BUILD_BANK"
    position: PositionCommand
