import sys
from shared.game.exception_codes import *

class GameException(Exception):
    exception_code: str = -1

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'GameError CODE: {self.exception_code}; {self.message}'
        else:
            return f'GameError CODE: {self.exception_code}'


class PositionIsAlreadyBusyException(GameException):
    exception_code = POSITION_ALREADY_BUSY


class NotEnoughCoinsException(GameException):
    exception_code = NOT_ENOUGH_COINS


class UnregisteredUserIdException(GameException):
    exception_code =  UNREGISTERED_USER_ID


class GameObjectPermissionDeniedException(GameException):
    exception_code = GAME_OBJECT_PERMISSION_DENIED


class IncorrectMovementPositionException(GameException):
    exception_code = INCORRECT_MOVEMENT_POSITION


class StartCellMustContainWarriorsException(GameException):
    exception_code = START_CELL_MUST_CONTAIN_WARRIORS


class CommandNotFound(GameException):
    exception_code = COMMAND_NOT_FOUND