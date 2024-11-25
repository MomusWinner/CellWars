from aiogram.filters.callback_data import CallbackData

MATCHMAKING_INLINE = {
    "text": "Начать поиск матча",
    "callback_data": "matchmake",
}

STATS_INLINE = {
    "text": "Посмотреть статистику",
    "callback_data": "stats",
}

CANCEL_MATCHMAKING_INLINE = {
    "text": "Отмена",
    "callback_data": "cancel_matchmaking",
}


class FieldCallback(CallbackData, prefix="field"):
    cell_x: int
    cell_y: int
    type: str
