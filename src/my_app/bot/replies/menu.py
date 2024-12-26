from aiogram.types import InlineKeyboardMarkup

from my_app.bot.handlers.buttons import MATCHMAKING_INLINE


def start_menu() -> tuple[str, InlineKeyboardMarkup]:
    matchmaking = MATCHMAKING_INLINE.export()

    markup = InlineKeyboardMarkup(inline_keyboard=[[matchmaking]])

    return "Привет!", markup
