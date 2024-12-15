from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from my_app.bot.composables.actions import add_cancel_button, add_field_actions
from my_app.bot.composables.field import (
    render_available_bank_placements,
    render_available_warrior_placements,
    render_field,
)
from my_app.bot.handlers.buttons import (
    CANCEL_FIELD_INLINE,
    PLACE_BANK_INLINE,
    PLACE_WARRIORS_INLINE,
)
from my_app.bot.types.callbacks import PlacementCallback
from my_app.bot.types.game import GameMessage
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    json_to_game_world,
)

from .router import router


@router.callback_query(PLACE_WARRIORS_INLINE())
async def warrior_placement_intent_handler(
    callback_query: CallbackQuery,
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return

    game_message = GameMessage.from_markup(message.text, reply_markup)
    available_places = render_available_warrior_placements(game_message)

    game_message.actions = []
    with_cancel = add_cancel_button(available_places)

    await message.edit_reply_markup(reply_markup=with_cancel.export_markup())


@router.callback_query(PLACE_BANK_INLINE())
async def bank_placement_intent_handler(
    callback_query: CallbackQuery,
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return

    game_message = GameMessage.from_markup(message.text, reply_markup)
    available_places = render_available_bank_placements(game_message)

    game_message.actions = []
    with_cancel = add_cancel_button(available_places)

    await message.edit_reply_markup(reply_markup=with_cancel.export_markup())


@router.callback_query(CANCEL_FIELD_INLINE())
async def cancel_placement_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    if not isinstance(callback_query.message, Message):
        await callback_query.answer("what")
        return

    message = callback_query.message
    reply_markup = message.reply_markup
    if reply_markup is None or message.text is None:
        return

    data = await state.get_data()
    game_world_json: str = data["game_world"]
    game_world = json_to_game_world(game_world_json)
    user_tag: int = data["user_tag"]

    field_buttons = render_field(game_world, user_tag)

    with_actions = add_field_actions(GameMessage.from_field(field_buttons))

    await message.edit_reply_markup(reply_markup=with_actions.export_markup())
