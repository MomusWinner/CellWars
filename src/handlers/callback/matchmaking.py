import aio_pika
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F

from src.handlers.buttons import CANCEL_MATCHMAKING_INLINE, MATCHMAKING_INLINE, STATS_INLINE
from src.handlers.states.game import GameGroup
from src.handlers.states.menu import MenuGroup

from .router import router


@router.callback_query(F.data == MATCHMAKING_INLINE["callback_data"])
async def start_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(GameGroup.matchmaking)
    cancel = InlineKeyboardButton(
        text=CANCEL_MATCHMAKING_INLINE["text"], callback_data=CANCEL_MATCHMAKING_INLINE["callback_data"]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[cancel]])
    await callback_query.message.edit_text("Ищем матч", reply_markup=markup)
    await callback_query.answer()

    async with channel_pool.acquire() as channel:
        channel: aio_pika.Channel
        queue = await channel.declare_queue("matches")


@router.callback_query(F.data == CANCEL_MATCHMAKING_INLINE["callback_data"])
async def cancel_matchmaking(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MenuGroup.start)
    matchmaking = InlineKeyboardButton(
        text=MATCHMAKING_INLINE["text"], callback_data=MATCHMAKING_INLINE["callback_data"]
    )
    stats = InlineKeyboardButton(text=STATS_INLINE["text"], callback_data=STATS_INLINE["callback_data"])
    markup = InlineKeyboardMarkup(inline_keyboard=[[matchmaking], [stats]])

    await callback_query.message.edit_text('Привет!', reply_markup=markup)
