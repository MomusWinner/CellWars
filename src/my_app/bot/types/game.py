from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from my_app.bot.utils.field import get_type, map_available_placements, rotate_coordinates
from my_app.shared.game.game_logic.core import GameObject, GameWorld


class GameTGMessage:
    info: str
    actions: list[list[InlineKeyboardButton]]
    field: list[list[InlineKeyboardButton]]

    def __init__(
        self,
        info: str | None,
        actions: list[list[InlineKeyboardButton]] | None,
        field: list[list[InlineKeyboardButton]] | None,
    ):
        self.info = info if info else ""
        self.actions = actions if actions else []
        self.field = field if field else []

    @classmethod
    def from_markup(cls: type["GameTGMessage"], info: str, markup: InlineKeyboardMarkup) -> "GameTGMessage":
        return cls.from_buttons(info=info, buttons=markup.inline_keyboard)

    @classmethod
    def from_buttons(
        cls: type["GameTGMessage"], info: str, buttons: list[list[InlineKeyboardButton]]
    ) -> "GameTGMessage":
        actions: list[list[InlineKeyboardButton]] = []
        field: list[list[InlineKeyboardButton]] = []
        for i, row in enumerate(buttons):
            if row[0].callback_data is not None and not row[0].callback_data.startswith("action"):
                actions = buttons[:i]
                field = buttons[i:]
                break

        return cls(info, actions, field)

    @classmethod
    def from_field(cls: type["GameTGMessage"], field: list[list[InlineKeyboardButton]]) -> "GameTGMessage":
        return cls(info=None, actions=None, field=field)

    @classmethod
    def empty(cls: type["GameTGMessage"]) -> "GameTGMessage":
        return cls(info=None, actions=None, field=None)

    def export_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.actions + self.field)
