import aio_pika
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from my_app.bot.types.callbacks import MovementCallback
from my_app.bot.types.game import GameTGMessage
from my_app.bot.utils.field import rotate_coordinates
from my_app.bot.utils.rabbit import publish_message
from my_app.shared.game.game_logic.command import PositionCommand, create_move_warriors_command
from my_app.shared.rabbit.game import GAME_EXCHANGE, GAME_QUEUE
from my_app.shared.schema.messages.game import create_game_message
from .router import router
from aiogram import F


@router.callback_query(
    MovementCallback.filter(F.type == "bank"), F.message.as_("message"), F.reply_markup.as_("reply_markup")
)
async def move_warriors_handler(
    callback_query: CallbackQuery,
    callback_data: MovementCallback,
    state: FSMContext,
    message: Message,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    data = await state.get_data()
    room_id: str = data["room_id"]
    user_tag: int = data["user_tag"]
    warrior_place: tuple[int, int] = data["warrior_place"]  # (y, x)

    if message.text is None:
        return

    game_tg_message = GameTGMessage.from_markup(message.text, reply_markup)

    point_from_rotated = rotate_coordinates(warrior_place, game_tg_message.field, user_tag)
    position_from: PositionCommand = {"x": point_from_rotated[0], "y": point_from_rotated[1]}

    point_to = (callback_data.cell_y, callback_data.cell_x)
    point_to_rotated = rotate_coordinates(point_to, game_tg_message.field, user_tag)
    position_to: PositionCommand = {"x": point_to_rotated[0], "y": point_to_rotated[1]}

    await publish_message(
        create_game_message(
            room_id,
            create_move_warriors_command(
                callback_query.from_user.id,
                PositionCommand(x=position_from["x"], y=position_from["y"]),
                PositionCommand(x=position_to["x"], y=position_to["y"]),
            ),
        ),
        GAME_QUEUE,
        GAME_EXCHANGE,
    )
    await callback_query.answer()
