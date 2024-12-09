from my_app.shared.game.exception_codes import (
    COMMAND_NOT_FOUND,
    GAME_OBJECT_PERMISSION_DENIED,
    INCORRECT_MOVEMENT_POSITION,
    INCORRECT_ZONE,
    NOT_ENOUGH_COINS,
    NOT_YOUR_STEP,
    POSITION_ALREADY_BUSY,
    START_CELL_MUST_CONTAIN_WARRIORS,
    UNREGISTERED_USER_ID,
)


class GameException(Exception):
    exception_code: int = -1

    def __init__(self, message: str | None = None) -> None:
        self.message = message

    def __str__(self) -> str:
        if self.message:
            return f"GameError CODE: {self.exception_code}; {self.message}"
        else:
            return f"GameError CODE: {self.exception_code}"


class PositionIsAlreadyBusyException(GameException):
    exception_code = POSITION_ALREADY_BUSY


class NotEnoughCoinsException(GameException):
    exception_code = NOT_ENOUGH_COINS


class UnregisteredUserIdException(GameException):
    exception_code = UNREGISTERED_USER_ID


class GameObjectPermissionDeniedException(GameException):
    exception_code = GAME_OBJECT_PERMISSION_DENIED


class IncorrectMovementPositionException(GameException):
    exception_code = INCORRECT_MOVEMENT_POSITION


class StartCellMustContainWarriorsException(GameException):
    exception_code = START_CELL_MUST_CONTAIN_WARRIORS


class CommandNotFound(GameException):
    exception_code = COMMAND_NOT_FOUND


class IncorrectZone(GameException):
    exception_code = INCORRECT_ZONE


class NotYourStep(GameException):
    exception_code = NOT_YOUR_STEP
