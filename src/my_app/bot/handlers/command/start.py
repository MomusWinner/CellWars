from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from my_app.bot.handlers.callback.router import router
from my_app.bot.handlers.states.menu import MenuGroup
from my_app.bot.replies.menu import start_menu


@router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.set_state(MenuGroup.start)
    text, markup = start_menu()
    sent_message = await message.answer(text, reply_markup=markup)
    await state.update_data(main_message=sent_message.message_id)
