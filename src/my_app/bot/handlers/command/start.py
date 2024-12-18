from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..buttons import MATCHMAKING_INLINE, STATS_INLINE
from ..states.menu import MenuGroup
from .router import router


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.set_state(MenuGroup.start)

    # callback buttons
    matchmaking = InlineKeyboardButton(
        text=MATCHMAKING_INLINE["text"], callback_data=MATCHMAKING_INLINE["callback_data"]
    )
    stats = InlineKeyboardButton(text=STATS_INLINE["text"], callback_data=STATS_INLINE["callback_data"])
    markup = InlineKeyboardMarkup(inline_keyboard=[[matchmaking], [stats]])

    await message.answer('Привет!', reply_markup=markup)
