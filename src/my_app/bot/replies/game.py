from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from my_app.bot.handlers.buttons import CANCEL_MATCHMAKING_INLINE


def search_match() -> tuple[str, InlineKeyboardMarkup]:
    cancel = CANCEL_MATCHMAKING_INLINE.export()

    markup = InlineKeyboardMarkup(inline_keyboard=[[cancel]])
    return "Ищем матч", markup
