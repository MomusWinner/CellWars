from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from my_app.bot.utils.rabbit import publish_message
from my_app.shared.schema.messages.match import create_match_message
from my_app.bot.handlers.buttons import CANCEL_MATCHMAKING_INLINE, MATCHMAKING_INLINE
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.handlers.states.menu import MenuGroup
from my_app.bot.replies.game import search_match
from my_app.bot.replies.menu import start_menu
from my_app.shared.rabbit.matchmaking import (
    MATCHES_QUEUE,
    MATCHMAKER_MATCH_EXCHANGE,
)

from .router import router


@router.callback_query(MATCHMAKING_INLINE(), F.message.as_("message"))
async def start_matchmaking(callback_query: CallbackQuery, state: FSMContext, message: Message) -> None:
    await state.set_state(GameGroup.matchmaking)

    user_id = callback_query.from_user.id
    text, markup = search_match()

    await message.edit_text(text, reply_markup=markup)
    await callback_query.answer()
    await state.update_data(message_id=message.message_id)
    await state.update_data(chat_id=message.chat.id)

    await publish_message(
        create_match_message(user_id=user_id, action="search"), MATCHES_QUEUE, MATCHMAKER_MATCH_EXCHANGE
    )


@router.callback_query(CANCEL_MATCHMAKING_INLINE(), F.message.as_("message"))
async def cancel_matchmaking(callback_query: CallbackQuery, state: FSMContext, message: Message) -> None:
    await state.set_state(MenuGroup.start)
    text, markup = start_menu()
    user_id = callback_query.from_user.id

    await publish_message(
        create_match_message(user_id=user_id, action="stop_search"), MATCHES_QUEUE, MATCHMAKER_MATCH_EXCHANGE
    )

    await message.edit_text(text, reply_markup=markup)
