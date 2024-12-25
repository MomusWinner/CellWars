from re import Match

from aiogram import Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from my_app.bot.handlers.states.game import PlacementGroup
from my_app.bot.types.game import GameTGMessage
from my_app.bot.types.renderers import WarriorsRenderer
from my_app.bot.utils.field import rotate_coordinates
from my_app.bot.utils.rabbit import publish_message
from my_app.shared.game.game_logic.command import PositionCommand, create_buy_warriors_command
from my_app.shared.game.game_logic.game_main import GameObjectFabric
from my_app.shared.game.game_logic.serialize_deserialize_game_world import json_to_game_world
from my_app.shared.rabbit.game import GAME_EXCHANGE, GAME_QUEUE
from my_app.shared.schema.messages.game import create_game_message

from .router import router


@router.message(
    PlacementGroup.warriors, F.text.cast(int) > 0, F.text.cast(int).as_("count"), F.from_user.id.as_("user_id")
)
async def warrior_count_handler(
    message: Message, bot: Bot, state: FSMContext, count: int, user_id: int, correlation_id: str
) -> None:
    await message.delete()
    data = await state.get_data()

    room_id: str = data["room_id"]
    user_tag: int = data["user_tag"]

    warrior_place: tuple[int, int] = data["warrior_place"]  # (y, x)

    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)

    point_rotated = rotate_coordinates(warrior_place, game_world.cells, user_tag)
    position: PositionCommand = {"x": point_rotated[0], "y": point_rotated[1]}

    warriors_count = count
    if warriors_count * GameObjectFabric.warrior_price > game_world.player_by_tag[user_tag].stats.coins:
        origin_message_id: int = data["message_id"]

        game_message = GameTGMessage.empty()
        WarriorsRenderer(game_message, game_world).add_ins_fun_info(user_tag)

        try:
            await bot.edit_message_text(text=game_message.info, message_id=origin_message_id, chat_id=user_id)
            return
        except TelegramBadRequest:
            return

    await publish_message(
        create_game_message(
            room_id=room_id,
            command=create_buy_warriors_command(
                user_id=user_id,
                count=warriors_count,
                position=position,
            ),
        ),
        GAME_QUEUE,
        GAME_EXCHANGE,
        correlation_id,
    )


@router.message(PlacementGroup.warriors)
async def delete_wrong_messages(message: Message) -> None:
    await message.delete()
