from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from my_app.bot.handlers.buttons import CANCEL_MATCHMAKING_INLINE


def search_match() -> tuple[str, InlineKeyboardMarkup]:
    cancel = InlineKeyboardButton(
        text=CANCEL_MATCHMAKING_INLINE["text"], callback_data=CANCEL_MATCHMAKING_INLINE["callback_data"]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[cancel]])
    return "Ищем матч", markup
