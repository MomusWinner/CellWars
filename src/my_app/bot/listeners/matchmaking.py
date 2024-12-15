import aio_pika
import msgpack
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from my_app.bot.composables.actions import add_field_actions
from my_app.bot.composables.field import render_field
from my_app.bot.composables.info import game_info
from my_app.bot.handlers.states.game import GameGroup
from my_app.bot.storage.rabbit import channel_pool
from my_app.bot.types.game import GameMessage
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)
from my_app.shared.rabbit.matchmaking import USER_MATCH_QUEUE_KEY
from my_app.shared.schema.messages.match import RoomCreatedMessage


async def listen_matches(bot: Bot, storage: BaseStorage):
    channel: aio_pika.Channel
    async with channel_pool.acquire() as channel:
        user_queue = await channel.declare_queue(USER_MATCH_QUEUE_KEY, durable=True)
        async with user_queue.iterator() as user_queue_iter:
            async for message in user_queue_iter:
                async with message.process():
                    body: RoomCreatedMessage = msgpack.unpackb(message.body)
                    game_world = json_to_game_world(body["game_world"])
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

                        if player.user_id == body["user_id_turn"]:
                            await state.set_state(GameGroup.player_turn)
                            field_markup = add_field_actions(
                                GameMessage.from_field(render_field(game_world, tag))
                            )
                        else:
                            await state.set_state(GameGroup.enemy_turn)
                            field_markup = GameMessage.from_field(
                                render_field(game_world, tag)
                            )

                        info = game_info(
                            game_world,
                            player.user_id == body["user_id_turn"],
                        )
                        await bot.edit_message_text(
                            text=info,
                            reply_markup=field_markup.export_markup(),
                            chat_id=chat_id,
                            message_id=message_id,
                        )

                        await state.update_data(room_id=body["room_id"])
                        await state.update_data(user_tag=tag)
                        await state.update_data(game_world=body["game_world"])
