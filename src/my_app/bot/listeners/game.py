import aio_pika
from aiogram.types import InlineKeyboardButton
import msgpack
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from my_app.bot.composables.actions import add_field_actions
from my_app.bot.composables.field import render_field
from my_app.bot.composables.info import game_info
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.storage.rabbit import channel_pool
from my_app.bot.types.game import GameTGMessage
from my_app.shared.game.game_logic.game_main import GameStates
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)
from my_app.shared.rabbit.game import GAME_INFO_QUEUE
from my_app.shared.schema.messages.game import GameInfoMessage


async def listen_turns(bot: Bot, storage: BaseStorage):
    channel: aio_pika.Channel
    async with channel_pool.acquire() as channel:
        turn_queue = await channel.declare_queue(GAME_INFO_QUEUE, durable=True)
        async with turn_queue.iterator() as turn_queue_iter:
            async for message in turn_queue_iter:
                async with message.process():
                    body: GameInfoMessage = msgpack.unpackb(message.body)
                    print(body)
                    match body["game_state"]:
                        case GameStates.RUN.value:
                            game_world_string = body["game_world"]
                            if not isinstance(game_world_string, str):
                                raise Exception("the game world is not a string")
                            game_world = json_to_game_world(game_world_string)

                            for tag, player in game_world.player_by_tag.items():
                                state = FSMContext(
                                    storage=storage,
                                    key=StorageKey(
                                        bot_id=bot.id,
                                        chat_id=player.user_id,
                                        user_id=player.user_id,
                                    ),
                                )
                                state_data = await state.get_data()
                                chat_id: str = state_data["chat_id"]
                                message_id: int = state_data["message_id"]
                                game_tg_message = GameTGMessage.from_buttons(
                                    game_info(game_world, body["user_id_turn"] == player.user_id),
                                    render_field(game_world, tag),
                                )

                                if body["user_id_turn"] == player.user_id:
                                    await state.set_state(GameGroup.player_turn)
                                    add_field_actions(game_tg_message)
                                else:
                                    await state.set_state(GameGroup.enemy_turn)

                                await bot.edit_message_text(
                                    game_tg_message.info,
                                    reply_markup=game_tg_message.export_markup(),
                                    chat_id=chat_id,
                                    message_id=message_id,
                                )

                                await state.update_data(game_world=body["game_world"])

                        case _:
                            return
