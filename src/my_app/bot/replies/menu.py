from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from my_app.bot.handlers.buttons import MATCHMAKING_INLINE, STATS_INLINE


def start_menu() -> tuple[str, InlineKeyboardMarkup]:
    matchmaking = InlineKeyboardButton(
        text=MATCHMAKING_INLINE["text"], callback_data=MATCHMAKING_INLINE["callback_data"]
    )
    stats = InlineKeyboardButton(text=STATS_INLINE["text"], callback_data=STATS_INLINE["callback_data"])
    markup = InlineKeyboardMarkup(inline_keyboard=[[matchmaking], [stats]])

    return "Привет!", markup
