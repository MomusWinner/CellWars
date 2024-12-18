from typing import TypedDict


class PositionCommand(TypedDict):
    x: int
    y: int


class GameCommand(TypedDict):
    user_id: int
    command_name: str


class MoveWarriorsCommand(GameCommand):
    move_from: PositionCommand
    move_to: PositionCommand


class BuyWarriorsCommand(GameCommand):
    position: PositionCommand
    count: int


class BuildBank(GameCommand):
    position: PositionCommand


def create_move_warriors_command(
    user_id: int, move_from: PositionCommand, move_to: PositionCommand
) -> MoveWarriorsCommand:
    return MoveWarriorsCommand(command_name="MOVE_WARRIORS", user_id=user_id, move_to=move_to, move_from=move_from)


def create_buy_warriors_command(user_id: int, position: PositionCommand, count: int) -> BuyWarriorsCommand:
    return BuyWarriorsCommand(command_name="BUY_WARRIORS", user_id=user_id, position=position, count=count)


def create_build_bank_command(user_id: int, position: PositionCommand) -> BuildBank:
    return BuildBank(command_name="BUILD_BANK", user_id=user_id, position=position)
