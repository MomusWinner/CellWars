from aiogram.filters.callback_data import CallbackData


class BaseCallback(CallbackData, prefix="base"):
    action: str


class ActionCallback(BaseCallback, prefix="action"):
    pass


class MenuCallback(BaseCallback, prefix="menu"):
    pass


class FieldCallback(CallbackData, prefix="field"):
    cell_x: int
    cell_y: int
    type: str


class PlacementCallback(FieldCallback, prefix="place"):
    pass


class MovementCallback(FieldCallback, prefix="move"):
    pass
