from aiogram.utils.keyboard import InlineKeyboardBuilder
from my_app.bot.handlers.buttons import (
    CANCEL_FIELD_INLINE,
    PLACE_BANK_INLINE,
    PLACE_WARRIORS_INLINE,
)
from my_app.bot.types.game import GameTGMessage


def add_field_actions(game_message: GameTGMessage) -> GameTGMessage:
    actions = InlineKeyboardBuilder()
    actions.add(PLACE_WARRIORS_INLINE.export())
    actions.add(PLACE_BANK_INLINE.export())
    buttons = actions.export()

    game_message.actions = buttons
    return game_message


def add_cancel_button(
    game_message: GameTGMessage,
) -> GameTGMessage:
    cancel_button = [[CANCEL_FIELD_INLINE.export()]]

    game_message.actions.extend(cancel_button)
    return game_message


# def add_warrior_actions(x: int, y: int, field_keyboard_builder: KeyboardBuilder) -> KeyboardBuilder:
# def add_bank_actions(x: int, y: int, field_keyboard_builder: KeyboardBuilder) -> KeyboardBuilder:
